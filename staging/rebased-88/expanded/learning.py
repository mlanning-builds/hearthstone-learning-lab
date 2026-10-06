"""Sparse action-conditioned softmax baseline; no implicit training runs.

The caller supplies one feature map per legal action and an externally computed
advantage. Observation encoding, returns, opponent sampling and checkpoints are
separate concerns. This linear baseline is not a claim of optimal play.
"""
import math
import random


class SparsePolicy:
    def __init__(self,*,seed,weights=None):
        self.rng=random.Random(seed)
        self.weights=dict(weights or {})
        if any(not isinstance(k,str) or not math.isfinite(v) for k,v in self.weights.items()):
            raise ValueError('Weights require string keys and finite values')

    @staticmethod
    def _validate(features):
        if not features:raise ValueError('At least one legal candidate is required')
        for row in features:
            if not isinstance(row,dict) or any(not isinstance(k,str) or not isinstance(v,(int,float)) or not math.isfinite(v) for k,v in row.items()):
                raise ValueError('Each action requires finite sparse numeric features')

    def probabilities(self,features):
        self._validate(features)
        scores=[sum(self.weights.get(k,0.0)*v for k,v in row.items()) for row in features]
        if any(not math.isfinite(s) for s in scores):raise ValueError('Nonfinite policy score')
        maximum=max(scores);values=[math.exp(s-maximum) for s in scores];total=sum(values)
        return [value/total for value in values]

    def choose(self,features):
        probabilities=self.probabilities(features);draw=self.rng.random();total=0.0
        for index,probability in enumerate(probabilities):
            total+=probability
            if draw<total:return index
        return len(probabilities)-1

    def reinforce(self,features,chosen,*,advantage,learning_rate):
        """One explicit on-policy gradient step; caller owns data/return validity."""
        probabilities=self.probabilities(features)
        if type(chosen) is not int or not 0<=chosen<len(features):raise ValueError('Invalid chosen action')
        if not math.isfinite(advantage) or not math.isfinite(learning_rate) or learning_rate<=0:
            raise ValueError('Finite advantage and positive learning rate required')
        gradient={}
        for index,row in enumerate(features):
            coefficient=(1.0 if index==chosen else 0.0)-probabilities[index]
            for key,value in row.items():gradient[key]=gradient.get(key,0.0)+coefficient*value
        updates={key:self.weights.get(key,0.0)+learning_rate*advantage*value for key,value in gradient.items()}
        if any(not math.isfinite(v) for v in updates.values()):raise ValueError('Nonfinite update; weights unchanged')
        self.weights.update(updates)
        return dict(chosen_probability=probabilities[chosen],updated_features=len(updates))

    def reinforce_batch(self,samples,*,learning_rate):
        """Sum episode gradients at one unchanged behavior policy, then commit.

        Samples are (feature_maps, chosen_index, return). No per-decision weight
        mutation, replay reuse, or length normalization. Caller ensures on-policy
        sampling. The sum is the undiscounted episodic score-function estimator.
        """
        if not math.isfinite(learning_rate) or learning_rate<=0:
            raise ValueError('Positive finite learning rate required')
        gradient={};count=0
        for features,chosen,advantage in samples:
            probabilities=self.probabilities(features)
            if type(chosen) is not int or not 0<=chosen<len(features):
                raise ValueError('Invalid chosen action')
            if not math.isfinite(advantage):raise ValueError('Nonfinite return')
            for index,row in enumerate(features):
                coefficient=advantage*((1.0 if index==chosen else 0.0)-probabilities[index])
                for key,value in row.items():
                    gradient[key]=gradient.get(key,0.0)+coefficient*value
            count+=1
        updates={key:self.weights.get(key,0.0)+learning_rate*value
                 for key,value in gradient.items()}
        if any(not math.isfinite(v) for v in updates.values()):
            raise ValueError('Nonfinite batch update; weights unchanged')
        self.weights.update(updates)
        return dict(samples=count,updated_features=len(updates))
