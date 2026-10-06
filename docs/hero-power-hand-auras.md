# Live hand-size Hero Power cost auras

Quel'dorei Fletcher (TIME_606) uses a shared data table of maximum hand size and Hero Power cost. A friendly, living, unsilenced source sets the cost to zero at three or fewer cards. Drawing, playing, Silence and removal automatically change legality, payment and visible cost through the same evaluator. It does not grant extra uses.

Source: pinned cards.json, build 251952, TIME_606 text. No new card download or rotation change. Six regression scenarios cover the hand threshold, real play/draw, free payment, once-per-turn use, removal, multiple sources and public observation.

The current evaluator applies live auras before next-use modifiers. That combined ordering is explicitly unverified (hero_power_hand_aura_order); these fixtures establish basic Fletcher behavior only, not full cost-system conformance.
