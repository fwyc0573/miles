# Miles Training and Rollout

Vocabulary for the relationship between sampled student trajectories, teacher scoring and training validation.

## Language

**Student**:
The policy whose parameters are optimized and whose sampled outputs supply the learning targets in on-policy distillation.
_Avoid_: Producer when referring specifically to the model being trained.

**Teacher**:
The fixed model that scores the student's sampled outputs to provide a distillation signal.
_Avoid_: Reference policy when the model provides the distillation target rather than a regularization baseline.

**Training/inference consistency**:
Agreement between the training and rollout computations of the same student's token probabilities under identical weights, inputs and probability definitions.
_Avoid_: Teacher–student agreement, training success.

**Policy staleness**:
The version difference between the policy that sampled an output and the policy used to train on it.
_Avoid_: Numerical inconsistency when the difference is caused by parameter updates.

**Routing replay**:
Reuse of a mixture-of-experts student's sampled expert choices in the matching training computations.
_Avoid_: Trajectory replay, teacher routing reuse.

**Trajectory replay**:
Reuse of previously generated trajectories as learning data under an explicitly defined training objective.
_Avoid_: Routing replay.

**Total-token loss normalization**:
Normalization of the summed learning loss by the global count of eligible target tokens in the optimization batch.
_Avoid_: Mean of per-sequence means.

**Successful optimizer update**:
A completed parameter optimization step that is counted separately from attempted or skipped training iterations.
_Avoid_: Iteration count when it includes skipped updates.
