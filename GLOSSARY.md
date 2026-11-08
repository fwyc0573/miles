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

**Experiment cell**:
One specified combination of a student, a teacher and a learning protocol in an experiment matrix, independent of how many execution attempts it requires.
_Avoid_: Unqualified cell when it could mean a deployment reconcile unit, execution attempt.

**Training turn**:
One assistant response to be learned from, together with the preceding conversation that supplies its input context.
_Avoid_: Conversation when counting individual assistant responses.

**Replay bank**:
A fixed collection of generated trajectories whose original responses and behavior-policy evidence are reused across specified optimizer updates.
_Avoid_: Prompt pool, which supplies inputs rather than completed trajectories.

**Source conversation**:
One multi-turn conversation in a training dataset whose assistant responses supply training turns.
_Avoid_: Trajectory, traj, when referring to dataset conversations rather than generated outputs.

**Interleaved turn order**:
An order in which a fixed number of source conversations are open at once and each in turn contributes a block of its next training turns, always in ascending turn order; a finished conversation is replaced by the next one in dataset order.
_Avoid_: Streaming order, which opens one conversation at a time; random turn order, which does not keep a conversation's turns ascending.

## Distillation profile

**Distillation profile**:
The running record of distillation measurements over successful optimizer updates, kept for the whole update and for each source conversation and training turn.
_Avoid_: Profile without qualification, training image, profiler.

**RKL**:
The reverse KL divergence KL(student‖teacher), taken over what the student generates: it asks whether the teacher also tends to generate what the student often generates. In the distillation profile, KL without qualification means RKL.
_Avoid_: Forward KL or KL(teacher‖student) for this quantity; they measure the opposite direction.

**Turn observation**:
The KL and NLL measured for one training turn in one successful optimizer update, together with that turn's identity.
_Avoid_: Cell, element, sample, when referring to one measured value record.

**KL-best update**:
The update with the lowest KL, either for the whole run or for one source conversation; NLL is read at that update rather than having its own best.
_Avoid_: Best NLL, best checkpoint.

**KL trend**:
The change in KL between an update and an earlier update a fixed number of successful updates before it.
_Avoid_: Slope, progress.

**Recovery gap**:
The latest KL minus the KL at the KL-best update.
_Avoid_: Regret, recovery space.
