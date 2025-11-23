# PROMPTS RECORD FOR DOCUMENT IMPROVING

## 1

```plain
hello gpt. now you are my technical documentation assistant. your task is to help me improve the technical documentation files in my project repository.

I will provide you with the BASIC CONTEXT of the project, which exists in `.github/copilot-instructions.md`. You need to READ and THINK about it carefully.

Then, you are required to give recommendations on improving the BASIC CONTEXT documentation itself, at least 5 points.

You can evaluate the documentation from the following aspects:
- Clarity: Is the documentation clear and easy to understand? If not, how can it be improved?
- Timeliness: Is the information up-to-date? If not, how can it be improved?
- Demand: Does every part of the documentation serve a clear purpose? If not, how can it be improved?
- Structure: Is the documentation well-organized for LLMs to READ and UNDERSTAND? If not, how can it be improved?

Please provide your recommendations in Chinese (Simplified).

**ATTENTION**:
- Do NOT modify the BASIC CONTEXT directly. Just provide recommendations for improvement.
- If you have ANY questions about the BASIC CONTEXT, ASK ME FIRST before giving recommendations, ONE BY ONE.
```

## 2

```plain
Actually there is no documentations existing in the project repository because i think they are too heavy to maintain. instead, i want to use LLMs to help me generate documentations on demand. So for now it's a unachieved idea for us to try to REBUILD the whole documentation system with LLMs assistance.
So, now you need to REALIZE that we now are at the very beginning stage of this idea. and your task is to help me IMPROVE the BASIC CONTEXT documentation in `.github/copilot-instructions.md` so that it can better support our future documentation generation on demand.

Please give more specific and detailed recommendations on how to improve the BASIC CONTEXT documentation to better support our future documentation generation on demand.

You can do the task by following these steps:
1. Analyze the current BASIC CONTEXT documentation.
2. Devide the BASIC CONTEXT documentation into the CURRENT EXISTING PARTS and the MISSING PARTS that are needed for future documentation generation on demand.
3. Use your **THINKING** ability to judge which parts are TRULY NEEDED for future documentation generation on demand, and which parts are NOT NEEDED. You can give a RATING to each part (from 1 to 10) to indicate its importance level for future documentation generation on demand. Also, give the REASONING for your judgement, like "this part is useless for future documentation improving because it's out-dated......".
4. List your result of last step.
```

## 3

```plain
OK now you have given me your analysis result of the BASIC CONTEXT documentation in `.github/copilot-instructions.md` at one time.
Now please list them by the rating you have given to each part, from HIGH to LOW.
And then, provide me with each point in one conversation turn, so that I can ask questions about each point if I have any.
```

## 4

```plain
OK now let's focus on the MAPPING problem first.
I want you to move the MAPPING part of the BASIC CONTEXT documentation in `.github/copilot-instructions.md` to a NEW DOCUMENTATION FILE named `index.md` under the `docs/` folder.
The `index.md` file will serve as the ENTRY POINT of the whole documentation navigation system.

With these informations, please provide me with the GENERAL STRUCTURE of the `index.md` file.
You can do it by following these steps:
1. Analyze the MAPPING part of the BASIC CONTEXT documentation in `.github/copilot-instructions.md`.
2. Devide the MAPPING part into SEVERAL SUB-PARTS that are needed for the `index.md` file.
3. Use your **THINKING** ability to judge which sub-parts are TRULY NEEDED for the `index.md` file, and which sub-parts are NOT NEEDED. You can give a RATING to each sub-part (from 1 to 10) to indicate its importance level for the `index.md` file. Also, give the REASONING for your judgement, like "this sub-part is useless for the `index.md` file because it's out-dated......".
4. List your result of last step.
```

## 5

```plain
Good job! I think the point 1 to point 4 are NECESSARY for the `index.md` file.
Now you can start to DRAFT the `index.md` file based on these 4 points.
You can do it by following these steps:
1. For each point from point 1 to point 4, EXPAND it into a DETAILED SUBSECTION for the `index.md` file.
2. Use your **THINKING** ability to make sure each subsection is CLEAR and DETAILED enough for the `index.md` file.
3. Combine all subsections into the DRAFT of the `index.md` file.

For `index.md`, you can now edit it directly under the `docs/` folder in the project repository.
```

## 6

```plain
Well done! Now let's focus on the details of the `index.md` file.

## DOCUMENT NAMING

now i think there is no need to distinguish between `*_for_ai.md` and normal `*.md` documents anymore.
There is no need to specially name documents for LLMs, because all documents are for LLMs by default in our documentation system.
So please help me to REMOVE the `*_for_ai.md` naming convention from the `index.md` file.

## DECISION JOURNEY DOCUMENTS

as same as above, there is no need to specially name documents for decision journey like `*_decision_journey.md` anymore.
We can include the informations about decision making process in normal journey documents like `*_journey.md`.
So please help me to REMOVE the `*_decision_journey.md` naming convention from the `index.md` file.

## OPS DOCUMENTS

actually there is no `install.md` and `quick_start.md` documents existing in the project repository for now.
So please help me to REMOVE these two documents from the `index.md` file for now.

also the target readers of these two documents should not be clear, because the ops documents are for everyone, from normal users to developers to LLMs.
So please help me to REWRITE the description of these two documents in the `index.md` file to make the target readers more CLEAR.

## OTHER PROBLEMS

There are many questions unmentioned above existing in the `index.md` file, but they could be summarized as the classes of problems like the above.

So, your task is to HELP ME IDENTIFY and FIX all these problems in the `index.md` file, according to the principles mentioned above.

You can do it by following these steps:
1. Analyze the whole `index.md` file.
2. Identify all problems existing in the `index.md` file, like the problems mentioned above.
3. For each problem, provide a DETAILED SOLUTION to FIX it.
4. Finally, COMBINE all solutions to a COMPLETE REVISED DRAFT of the `index.md` file.
```

## 7

```plain
Well done!
Now you have reached the FINAL STEP of `index.md` file improving.
Now please review the COMPLETE REVISED DRAFT of the `index.md` file carefully.
You can do it by following these steps:
1. Read the COMPLETE REVISED DRAFT of the `index.md` file carefully.
2. Use your **THINKING** ability to JUDGE whether the COMPLETE REVISED DRAFT of the `index.md` file is CLEAR, DETAILED, and COMPLETE enough.
3. If you find ANY PROBLEMS in the COMPLETE REVISED DRAFT of the `index.md` file, PLEASE FIX THEM IMMEDIATELY.
4. Finally, PROVIDE the FINAL VERSION of the `index.md` file.

REMEMBER, in the last paragraph, the document mapping is CURRENTLY at the starting stage, which means there are actually no documentations existing in the project repository for now.
```

## 8

```plain
Well done!
Now we finished the task of improving the `index.md` file.
Please retell me the VERY-EARLY tasks we have done to improve the BASIC CONTEXT documentation in `.github/copilot-instructions.md`, including the recommendations you have given to me at the very beginning, the analysis you have done about the BASIC CONTEXT documentation, and so on.
Please tell me which steps we have done and which step to step in the next.
```

## 9

```plain
Great!
Now let's focus on the improving of the doc `status.md` under the `docs/` folder.
Please give me serveral recommendations on improving the `status.md` document.
You can do it by following these steps:
1. REVIEW what we did previously to ensure where we are now.
2. REVIEW the whole project repository to UNDERSTAND the CURRENT STATUS of the project.
3. Use your **THINKING** ability, give me the aspects that will be included in the `status.md` document to better reflect the CURRENT STATUS of the project.
4. For each aspect, provide a DETAILED EXPLANATION on why it should be included in the `status.md` document.

I've provided you with the metadata of the `status.md` document.
```

## 10

```plain
Excellent!
Most of your recommendations are very useful. Now i am gonna add more details into your recommendations.

## POINT 1
I think we could record 3 kinds of MILESTONES in the `status.md` document:
- ALREADY ACHIEVED MILESTONES, which reflect what we have already achieved in the project.
- CURRENTLY WORKING-ON MILESTONES, which reflect what we are working on now in the project.
- UPCOMING MILESTONES, which reflect what we are going to achieve in the near future in the project.

The importance of these 3 kinds of milestones are different, with the ALREADY ACHIEVED MILESTONES being the most important, and the UPCOMING MILESTONES being the least important.

## POINT 7
I think there is no need to specially mention the MAINTAINERS of the project in the `status.md` document, because the maintainers could be changed frequently. So actually you only need to make sure that, all document writers included human and LLMs, should write down their names in the metadata of `status.md` document when they make changes to it.

## OTHER POINTS

You should be well-known for which principles are exclusive to the `status.md` document, and which principles are common to all documents in the documentation system.
After finishing the `status.md` document improving task, we'll soon move to the `principles.md` document improving task, which writes down the COMMON PRINCIPLES for ALL documents in the documentation system.
So you should figure out which principles are EXCLUSIVE to the `status.md` document, and which principles are COMMON to ALL documents in the documentation system. (again)

With informations above, please edit `status.md` document to a COMPLETE and DETAILED version.
```

## 11

```plain
Not that bad! But I am going to correct some small mistakes in your `status.md` document draft.

## POINT 1
You suggested to add a section about current version and milestones. I think there is no need to specially mention these informations in the YAML metadata of the `status.md` document. Instead, we've just decided to add these informations (version, milestones, ...) in the main content of the `status.md` document.

## POINT 3
I think there is no need to specially mention the VERIFICATION STATUS of the project in the `status.md` document. As you know, our project is ONLY running on *RoboMaster EP/S1 robots* and *Raspberry Pi 4B computers*, but we use another PC as the development(coding) machine, so you need to clarify the idea that there is no need to TEST on DEVELOPMENT machines.
Also, currently we don't use AUTOMATED TESTING in our project, so there is no need to mention it in the `status.md` document.

## POINT 5
This idea is good, but you need to know that the DOCUMENTATION STATUS part is ONLY used for our recent rebuilding of the documentation system with LLMs assistance, so after the documentation system is rebuilt completely, there is no need to mention the DOCUMENTATION STATUS part in the `status.md` document anymore.

## POINT 6
I got this EXCELLENT idea! But it shouldn't be written in the `status.md` document. Instead, it should be written in a NEW DOCUMENT named `plans.md` under the `docs/` folder, which writes down plans and ideas for the future development of the project.

The idea could be devided into 2 parts:
- SHORT-TERM PLANS, which writes down the plans and ideas for the near future development of the project.
- LONG-TERM VISION, which writes down the long-term vision and goals of the project.

## POINT 7
This idea is also good, but it should be written in a NEW DOCUMENT named `principles.md` under the `docs/` folder, which writes down the COMMON PRINCIPLES for ALL documents in the documentation system because it's more like a kind of principles instead of some specific status of the project.

With informations above, please revise the `status.md` document to a FINAL VERSION. I'll check it after you finish it.
```

## 12

```plain
You seems not to understand my previous instructions well.
I said that we SHOULD NOT do verification on DEVELOPMENT machines, because the project is ONLY running on *RoboMaster EP/S1 robots* and *Raspberry Pi 4B computers*. Verification and the testing results should be wriiten by HUMANS after their real-world, personal tests on the target hardware platforms. We should not focus on if the project can run on DEVELOPMENT machines, because it's meaningless.

Also, I said that we DON'T use AUTOMATED TESTING in our project currently, so there is no need to mention it in the `status.md` document.

## Point 5

What does it mean? You did not mention this part in your previous draft of `status.md` document. Or, is it something that you have added newly in this revision? Please clarify it.

## Point 7
This is not what `status.md` document is for. As I have said before, the COMMON PRINCIPLES for ALL documents in the documentation system should be written in a NEW DOCUMENT named `principles.md` under the `docs/` folder.

With informations above, please use your **THINKING** ability to organise the `status.md` document again, and write down contents in `status.md` under `docs/` folder. I'll check it after you finish it.
```

## 13

```plain
Well done! We have now finished the improving task of `status.md` document.
Now please review the WHOLE documentation system again, including the `index.md` and `status.md` documents under the `docs/` folder. After reviewing, give me your opinions about the next steps we should take to improve the documentation system further.
```

## 14

```plain
Ok i got it.
Now we can step into the next task of improving the `principles.md` document under the `docs/` folder.

Please READ EVERY SINGLE LINE of the ENTIRE project repository carefully, including the source code files, the existing documentation files, the issue tracker, the pull request history, and so on.

After that, use your **THINKING** ability to summarize serveral COMMON PRINCIPLES that are used in *DOCUMENT WRITING*, *CODE WRITING*, *TESTING*, and *PROJECT MANAGEMENT* in this project.

Then, write down these COMMON PRINCIPLES in a NEW DOCUMENT named `principles.md` under the `docs/` folder DIRECTLY.
```

## 15

```plain
Well done! I think it's good enough for now.
Now please review the WHOLE `status.md` document again carefully. I found some small problems in it.
After your reading, i will tell you.
```

## 16

```plain
I've just edited the `status.md` document under the `docs/` folder to fix some small problems in it.
Please READ `status.md` carefully again, and tell me what you think about my changes.
```

## 17

```plain
I think the suggestions about _TODO is not necessary, so you can forget it.

Now let's focus on `principles.md` document under the `docs/` folder.
Please review the WHOLE `principles.md` document carefully again. I've just changed some details in it.
After your reading, tell me what you think about my changes.
```

## 18

```plain
Great understanding!
Now let's step into the next task of improving the `plans.md` document under the `docs/` folder.

- Please READ EVERY SINGLE LINE of the ENTIRE project repository carefully again, including the source code files, the existing documentation files, and so on.

During your reading, use your **THINKING** ability to figure out what we have done yet, what we are doing now, and what we seem to do in the near future in this project. ( If you cannot figure out the future part it's ok, just focus on the past and present parts )

- Then, write down these informations in a NEW DOCUMENT named `plans.md` under the `docs/` folder DIRECTLY.

If you have any questions, ASK ME FIRST before writing the `plans.md` document. ONE BY ONE(which means you can only ask one question at a time).
```

## 19

```plain
Good job!
Now please review EVERY SINGLE LINE of the WHOLE project repository again, including the source code files, the existing documentation files, and so on.
Then, review EVERY SINGLE LINE of the documentation system under the `docs/` folder again, including the `index.md`, `status.md`, `principles.md`, and `plans.md` documents.

After your reading, give me your opinions about the OVERALL DOCUMENTATION SYSTEM, including its STRENGTHS and WEAKNESSES, and the NEXT STEPS we should take to improve the documentation system further.

You can evaluate it from the following aspects:
- ACCURACY: Could EVERY WORDS in the documentation system be corresponding to the existing files in the project repository? Tell me if you find ANY INACCURACIES.
- COMPLETENESS: Does the documentation system cover ALL IMPORTANT PARTS of the project repository? Tell me if you find ANY MISSING PARTS.
- And so on.
```

## 20

```plain
Ok i just copied the entire `documents/` folder which is used in the previous branch `dev_v1_1` to the local directory.
Now please READ EVERY SINGLE LINE of the OLD DOCUMENTATION SYSTEM under the `old_docs/documents/` folder carefully, including ALL `.md` files in it.
Then, use your **THINKING** ability to summarize the DETAILED CONTENTS of the OLD DOCUMENTATION SYSTEM. Give me your summary.
Then, compare it with the CURRENT DOCUMENTATION SYSTEM under the `docs/` folder. Give me your comparison result, including the DIFFERENCES between these two documentation systems, the STRENGTHS and WEAKNESSES of the CURRENT DOCUMENTATION SYSTEM compared to the OLD DOCUMENTATION SYSTEM, and so on.
```

## 21

```plain
Good job!
Now we need to improve the CURRENT DOCUMENTATION SYSTEM under the `docs/` folder by LEVERAGING the structure of the OLD DOCUMENTATION SYSTEM under the `old_docs/documents/` folder.

**ATTENTION**:
The intention that i copied the old documentation system to the local direcotory is to let you have a sight of a un-well-organized documentation structure, so that you can learn from its mistakes and avoid making the same mistakes in the current documentation system.

So, in order to come up with a better documentation structure, please learn the old documentation system carefully by following these steps:
1. READ EVERY SINGLE LINE of the OLD DOCUMENTATION SYSTEM under the `old_docs/documents/` folder carefully, including ALL `.md` files in it.
2. Use your **THINKING** ability to IDENTIFY the benefits and drawbacks of the OLD DOCUMENTATION SYSTEM.
3. Based on your analysis result, provide me with a DETAILED STRUCTURE of the CURRENT DOCUMENTATION SYSTEM under the `docs/` folder, which LEVERAGES the benefits of the OLD DOCUMENTATION SYSTEM and AVOIDS its drawbacks.

REMEMBER: Not to copy the contents in the old documentation system directly, but to LEARN its structure to IMPROVE the current documentation system.
Most of the contents in the current documentation system are out-dated, so there is no reason to copy them directly currently.
```

## 22

```plain
Good. Now let's discuss about the details.
The discuss won't come to an end until i said "it's time to end the discussion.".
Each time you received `##` markdown header from me, you need to know that a new discussion point is coming.
You should **THINK** of the problems and the DETAILS **CAREFULLY**, and then provide me with your OPINIONS and SUGGESTIONS about the discussion point.
Now let's begin.

## `history` section

- You need to clarify that the `history` section in the current documentation system is used to record ALMOST EVERY DETAILS about the development history of the project, including the small changes and big changes, so that when we are facing any problems, we can easily go through the `history` section to find out the previous changes that may cause the problems, in order to fix the problems quickly.
- I STRONGLY SUGGEST that EVERY HISTORY RECORDING DOCUMENT should have a short introduction about its own history EXISTING in the YAML metadata of the document itself, so that we could JUMP OUT OF SOME IRRELEVANT CONTENTS to save tokens and time.

THERE ARE TWO SUGGESTIONS of the `history` section. Other suggestions may also exist, which are up to your thinking.
```

## 23

```plain
Your suggestions are all very good!
To prevent from forgetting, please write down your suggestions about the `history` section in a DRAFT of `tmp_structure_design.md` document under the `docs/` folder directly.
Then we can step into the next discussion point.
```

## 24

```plain
Before we step into the next discussion point, please RE-READ the ENTIRE documentation system under the `docs/` folder carefully, including the `index.md`, `status.md`, `principles.md`, and `plans.md` documents.

## `next_steps.md` document

Actually the plans in `next_steps.md` document are now out-dated, so there is no need to keep it anymore.
Instead, we have a new `plans.md` document under the `docs/` folder, which writes down the plans and ideas for the future development of the project.

## `reference` section

I think the `reference` section is very useful, so we need to keep it for sure.
But we also need to strengthen their own connections to the main documentation system under the `docs/` folder.
For example, we can add links in the `index.md` document under the `docs/` folder to point to the important documents in the `reference` section.

## `PERFORMANCE_OPTIMIZATION_HISTORY.md` document

Uh, actually this document is SO MESSY that I don't even want to improve it.
So I suggest you to try your best to merge the useful parts in it into `history` documents under the `docs/journey/` folder, and then DELETE this document directly.

## `image_preprocessing_history.md` document & `preprocessing_troubleshooting_history.md` document

This document is useless, so we can DELETE it directly.

## `development_history_v1.md` document

This document is a very valuable document, so we need to KEEP it for sure.
But we need to improve its contents to better suit to our current documentation system.

Understand?
```

## 25

```plain
Yeah please edit `tmp_structure_design.md` document under the `docs/` folder to include your suggestions above.
Then we READ THE END OF DISCUSSION.
Next your task is to DETAILEDLY READ the ENTIRE documentation system under the `docs/` folder carefully, including the `index.md`, `status.md`, `principles.md`, and `plans.md` documents.
Then you need to use your **THINKING** ability to come up with a solution about merging the OLD DOCUMENTATION SYSTEM STRUCTURE into the CURRENT DOCUMENTATION SYSTEM STRUCTURE under the `docs/` folder, **LIKE WE DISCUSSED BEFORE**.
After all, tell me about your solution.
```

## 26

```plain
Good job!
Now please create direcories and empty files under the `docs/` folder according to your solution.
After that, we can step into the next task of improving the contents of these files one by one.
```

## 27

```plain
Well done!
Let's finish `v1_0_history.md` document under the `docs/journey/` folder first.
```

## 28

```plain
Are you sure? The old development recording v1 document is very long and detailed, but the new v1_0_history.md document is very short and simple. Do you think the new v1_0_history.md document is DETAILED enough to cover the development history of v1.0 version?
```

```plain
...
```

## 29

```plain
Let's focus on some important details.

## Journey Classification

The different journey documents should be connected to different features or modules in the project.
For example, we can have `aimassistant_journey.md` for the aim assistant feature, `uart_communication_journey.md` for the uart communication module, and so on,
instead of having a `performance_journey.md` document that covers everything about performance optimizations like what you said.
```

## 30.

```plain
Well!

Now please edit `index.md` document under the `docs/` folder, to firstly structure the unwritten documents according to your solution, and then add links to these documents in the `index.md` document.

For example, we'll soon create `aimassistant_journey.md` document under the `docs/journey/` folder, so you need to add a link to this document in the `index.md` document under the `docs/` folder CURRENTLY BEFORE WE ACTUALLY CREATE IT in order to clarify the structure of the documentation system.
```
