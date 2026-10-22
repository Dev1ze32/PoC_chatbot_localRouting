# Dataset card: UC-PnC helpdesk QLoRA training set (sample, 5 examples)

Structure follows the dataset-card / datasheet practice (Gebru et al., *Datasheets for Datasets*, CACM 2021; Hugging Face dataset cards).

## 1. Purpose
Teach Llama 3.2 3B **how** to answer from retrieved handbook passages, not **what** the handbook says:
answer from the passages, cite them exactly, or refuse. The knowledge base can then change without retraining.

## 2. Files
| File | Contents |
|---|---|
| `train.jsonl` | What the trainer reads. One example per line: `id`, `type`, `prompt`, `completion`. |
| `build_report.md` | The evidence for each example: passages given and used, facts traced, citation check, changed facts. |
| `build_sample_set.py` | The recipe that builds and checks both files. |

## 3. Format
Conversational **prompt-completion** (TRL `SFTTrainer`):
- `prompt` = system prompt v4 + user message (3 retrieved passages + question), built by the same code as the live server.
- `completion` = the target answer.

The trainer computes the loss **only on the completion**. The model is never trained to reproduce the passages, only to answer from them.

## 4. Composition (example types)
| `type` | Target | Behaviour taught | Planned share |
|---|---|---|---|
| `answer_with_steps` | 1 sentence + numbered steps + `Source:` lines | answer how-to questions from the passages; skip distractors | ~40% |
| `answer_direct` | 1 sentence (+ short list) + `Source:` lines | answer a short question directly from the passage; pick the rule for the right group (e.g. students, not staff) | ~20% |
| `refuse_on_topic_no_answer` | decline sentence only | refuse when passages are on topic but don't answer | ~15% |
| `refuse_wrong_passages` | decline sentence only | refuse even for a question seen in training; the output follows the passages | ~15% |
| `answer_follow_edited_passage` | answer from a deliberately edited passage | follow the passage over memory (moving to the test set, pending your go) | ~10% |

## 5. How targets are written
1. Mark which passages answer the question. If none do, the target is the decline sentence.
2. Write sentence 1 and the list **only from the marked passages**, in their wording and order.
3. The script adds the `Source:` lines from the marked passages' headers. Nobody types them.
4. **Automatic check:** every number, time, form code and office name in the target must appear in the marked passages, or the build fails.
5. A person reviews every target against the handbook.

## 6. Design choice vs. RAFT (Zhang et al., 2024, arXiv:2403.10131)
Like RAFT, the examples include distractor passages. The difference:
- **RAFT:** when the right document is missing, the model is still trained to answer, which the authors say "compel[s] the model to memorize answers".
- **Here:** when the right passage is missing, the model is trained to **refuse**. This is deliberate, because this system must keep working when the handbook changes.

## 7. Splits
Validation and test are separate files, split by **handbook section**, so the test covers material never seen in training.

## 8. Limitations
- 5 examples: a design sample, not a training set.
- Changed-fact examples contain deliberately wrong figures (listed in `build_report.md`) and must never be used as a knowledge source.
- Some memorization can still happen. It is measured with the changed-fact and wrong-passage tests, and backed up by the server guardrails.
