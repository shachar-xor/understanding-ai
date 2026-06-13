# Understanding AI for Geeks — Speaking Transcript

A slide-by-slide script of what to say, with per-slide and running time estimates.
Written for the deck as it currently stands (33 slides, `understanding_ai_for_geeks.pptx`).

- Pace assumed: calm, conversational, with pauses for clicks and audience replies.
- Total body: **~32 minutes**. Add **~3-4 minutes** of Q&A for **~36 minutes** overall.
- Times in **(this slide / running total)**. "[click]" marks an animation reveal.

---

## SLIDE 1 — Title: "Understanding AI for Geeks"  (0:30 / 0:30)

> Let the slide sit for a second before you speak.

"Let's talk about AI. But not in the way you've probably heard it a hundred times already.

We're going to do it the way geeks do: take it apart, see how the pieces fit, and walk out actually understanding it."

> Pause, then move on.

---

## SLIDE 2 — About me  (0:45 / 1:15)

"Quick intro. Hi, I'm Shachar.

[click] I'm a software developer.

[click] I've been at Cato for over five years. That's me with the five-years-a-Catonian Lego tower.

[click] I'm a Lego and Office fan. Yes, that's my Dundie [click, Michael Scott appears], just like Michael's.

[click] And I'm a geek. Which is exactly what this talk is about."

---

## SLIDE 3 — I love to understand things  (1:00 / 2:15)

"As a geek, I've always understood things the same way.

[click] By building them up, like Lego.

[click] By breaking them down, like an M16 laid out in pieces.

[click] And by fixing what's broken. Yes, even our own CatoClient. (wink)

I've basically been doing this my whole life.

[click] So let's do exactly that with AI: take it apart, and learn to think with it and use it better."

---

## SLIDE 4 — The insight: we've done this before  (1:15 / 3:30)

"Here's the thing. AI is a new technology, but dealing with new technology is our home turf.

Every time a new paradigm showed up, *we* invented the words that made it thinkable. Object-orientation: encapsulation, inheritance, polymorphism. Design patterns: Singleton, Factory, Observer. SOLID. Functional programming. Cloud and microservices. Agile and DevOps.

Think about it: imagining a Singleton or a Factory isn't hard for an experienced developer. SOLID is second nature. And once we coined those terms, juniors and seniors could all think and talk about them. None of it came from one vendor. The community built it.

[click] We built the language for software. Now let's build one for AI."

---

## SLIDE 5 — We've done this before, as a community  (1:15 / 4:45)

"Same idea on a timeline.

[click] OOP in the seventies. [click] Design Patterns in '94. [click] Agile in 2001. [click] SOLID in 2004. [click] Cloud in 2006.

Every single shift, the community coined the vocabulary that made the idea shareable. No vendor handed it to us.

[click] AI is the next stop. And the words? We write those."

---

## SLIDE 6 — But AI is different  (1:15 / 6:00)

"There's a catch, though. AI takes away the two things that let us build a shared language last time.

[click] It's fast. New models, new terms, every few weeks. The words never get the years that 'Singleton' or 'SOLID' had to settle.

[click] And it's closed. It's vendor-driven and built for lock-in. OpenAI, Anthropic, Google, Meta, all competing. None of them is motivated to give us a shared vocabulary.

[click] So we build it ourselves. As a community, vendor-independent. We can't wait for it to settle, so let's start now."

---

## SLIDE 7 — We'll break AI into three pieces  (0:45 / 6:45)

"And we'll break AI into three pieces.

[click] The LLM, the core engine.

[click] The Agent: an LLM with tools and a loop, so it can actually take action.

[click] And Context Management: everything we feed it and manage around it.

Three equal parts of one whole. We'll take them one at a time."

---

## SLIDE 8 — LLM: just another ML algorithm  (0:45 / 7:30)

"First piece: the LLM. It just stands for Large Language Model.

Let's demystify it right away. It is not magic. It's just another machine learning algorithm.

[click] And for this whole talk, we are not going to open it up. We'll treat it as a black box: text goes in, text comes out."

---

## SLIDE 9 — LLM training stage  (1:15 / 8:45)

"The LLM has two phases. First, training, which happens once, up front.

It gets fed an enormous slice of everything people have written: books, code, Reddit, news, Wikipedia. And it learns the patterns in it.

Two things to keep in mind.

[click] One: that text is human. So it carries our mistakes, our opinions, our jokes, our memes, even deliberate trolling. It's a mirror of the corpus, not an oracle.

[click] Two: when training ends, it freezes. Its knowledge stops at that exact moment.

Then comes the second phase, operation, which is what we actually use."

---

## SLIDE 10 — LLM operation stage  (0:50 / 9:35)

"Operation is what happens every time you use it. And here's the whole secret: it just autocompletes text.

Look at the input: 'Cato Networks is the best SASE company in the ___.'

> Pause. Let the room fill it in. Most will say 'world'.

[click] 'Universe!'

It has read enough Cato marketing to complete it that way. It is not thinking. It's picking the most probable next words. That's the entire job."

---

## SLIDE 11 — It can be trivial, it can reason  (1:15 / 10:50)

"Now watch how far that one trick stretches.

On the left, pure pattern matching. [click] 'The sky is...' blue. [click] 'Dogs say...' woof. A small child completes these.

On the right, the *same* autocomplete, but now it's landing logic and physics. [click] 'All humans are mortal, Socrates is human, therefore Socrates is...' mortal. [click] 'I fly near light-speed to a star and back, next to my twin I aged...' less.

That twin-paradox answer doesn't come from reasoning. It comes from having read enough philosophy and physics text to know how those sentences end. The mechanism is trivial. The scale is not."

---

## SLIDE 12 — It knows a lot, up to a point  (1:00 / 11:50)

"It also knows a huge amount.

[click] Capital of Japan? Tokyo. [click] Romeo and... Juliet. [click] Water is hydrogen and... oxygen. Geography, literature, science, all from the training text.

But [click] it's frozen. Ask it about this morning's news, it can't know. [click] Ask about the latest model released, and it can only give you whatever was current when training ended. That moment has a name: the knowledge cutoff.

It learned the world once, and then it stopped."

---

## SLIDE 13 — It's not deterministic, it makes guesses  (1:00 / 12:50)

"It's also not deterministic.

'A good name for a coffee shop is...' [click] 'The Daily Grind.' Run it again, same prompt [click] 'Bean There, Done That.' Different answer, same question. It's sampling from probabilities.

And because it predicts likely text rather than looking things up: [click] ask for your account number, it'll just invent one. [click] Ask for the weather right now, it can't look. It can only guess.

Probability, not retrieval."

---

## SLIDE 14 — It can be subjective, it can be wrong  (1:15 / 14:05)

"It can be subjective, and it can be flat-out wrong.

On the left, ask for 'the best' anything. [click] Greatest band ever? The Beatles. [click] Best programming language? Python. Those are opinions: the majority view of the training text. There's no single truth in there.

On the right, watch this. [click] 'Who won the 1987 Tulsa chess championship?' [click] 'David Harrington, a local teacher who...'

[click] There was no 1987 Tulsa chess championship. The premise is false, so the confident answer is false too. It does not push back on a bad question. It just completes it.

Confident tone is not the same as being correct."

---

## SLIDE 15 — Every letter counts  (1:00 / 15:05)

"And it reads every single token.

'A cat walked into a library and asked for a book about...' [click] fish.

Now I change one letter. 'A *car* walked into a library and asked for a book about...' [click] roads and highways.

Same sentence, one letter apart, and the whole answer changes. This is why prompt wording matters so much. One letter early can steer the entire response."

---

## SLIDE 16 — It can role-play  (1:15 / 16:20)

"And here's the last trait, the one that sets up everything next: it can role-play.

[click] 'You are Gandalf, a level 12 wizard. Spells: Fireball, Detect Magic, Light. A Balrog blocks the bridge. Your move?' [click] 'I slam my staff down, you shall not pass, and ready Fireball.'

[click] Same trick, real job. 'You are a senior software engineer, you write clean secure Python, review this for a bug.' [click] 'First, the bug: this loop is O(n squared). Here's the fix, then why it works.'

Notice both prompts give it a *role* and a list of *capabilities*. That's exactly how the industry shaped the early system prompts.

But here's the catch: those spells, that terminal, they're just words. The model can't actually cast Fireball or run the code.

Give that role *real* tools and a loop, and you get the next layer."

---

## SLIDE 17 — Agent = LLM  (0:20 / 16:40)

"Layer two: the Agent.

At its core, an agent starts as just an LLM. It reads input and decides what to do, in text."

---

## SLIDE 18 — Agent = LLM + Tools  (0:25 / 17:05)

"Now add tools. Web search, a calculator, APIs.

The LLM doesn't run them. It just *decides* which one to call. The framework around it actually runs the tool."

---

## SLIDE 19 — Agent = LOOP( LLM + Tools )  (0:30 / 17:35)

"And then wrap the whole thing in a loop.

The tool result goes back to the LLM. It re-reads everything, decides the next step, and keeps going until it decides it's done."

---

## SLIDE 20 — The agent loop, full diagram  (1:00 / 18:35)

"Here's the full picture.

User input enters at the LLM, at the top. At the bottom, it asks one question: am I done? If yes, the output exits as the agent's answer. If no, it loops: call a tool, read the result, come back, and ask again.

One question goes in. Everything else happens inside the loop."

---

## SLIDE 21 — The developer wrote one question  (0:30 / 19:05)

"Let's make that concrete.

This is all the developer typed: 'Who is Taylor Swift's boyfriend? Find out his age and calculate the square root of his age.'

One question. [click] Now watch what the agent wraps around it."

---

## SLIDE 22 — The agent wraps it in context  (0:50 / 19:55)

"The agent didn't change the question. It wrapped it.

There's a system block: 'You are a helpful research assistant, search the web for facts, use the calculator for math, show your reasoning.' Then a list of tools. And then the original question, nested inside.

> Point at the tools list.

This right here is how the LLM knows what tools exist. It's just text. Not a function registry, not an API. A description.

[click] Let's watch the first call."

---

## SLIDE 23 — Call 1 of 4  (0:50 / 20:45)

"Call one. Everything is green, because it's all brand new.

The LLM reads top to bottom: I'm a research assistant, I have these tools, here's the question. It decides it needs to search, and it outputs a tool call, in text: web_search, Taylor Swift boyfriend.

And the key idea, on the right: the context grows every step, and the LLM re-reads all of it."

---

## SLIDE 24 — Call 2 of 4  (0:50 / 21:35)

"Call two. Now the colors mean something. Grey is what it's already seen. Amber is the previous LLM response. Green is the new tool result.

The search came back: Taylor Swift and Travis Kelce, confirmed in 2023. That result gets appended, and the *entire* context is sent again.

Notice: the LLM is never told it's on step two. It figures that out by re-reading from the top. It decides it now needs Kelce's age, and searches again."

---

## SLIDE 25 — Call 3 of 4  (0:45 / 22:20)

"Call three. Context keeps growing. Everything from calls one and two is still here, and still re-read.

Now it knows: the boyfriend is Kelce, age 35. What's left? The square root. So it switches tools, from web search to the calculator: sqrt of 35.

Still just text coming out."

---

## SLIDE 26 — Call 4 of 4  (1:00 / 23:20)

"Call four. The full history is dimmed behind us, and the new green is the calculator result and the final answer.

The LLM reads four calls' worth of context, sees the result, and decides: I have everything. No more tools.

Step back and count it. One question from the developer. Underneath: four LLM calls, two web searches, one calculator call. That is an agent."

---

## SLIDE 27 — Context is limited, we manage it  (1:30 / 24:50)

"Layer three: Context Management.

Here's an analogy. Human intelligence has no hard limit either. [click] But it needs resources: time, food, sleep, motivation. Starve it and performance drops.

[click] AI agents are the same, except what they mostly need is context. [click] And context fills up fast: a real agent does 20, 30, 50 steps, and the window fills quickly. [click] Larger context also costs significantly more.

[click] Now, every agent already manages some of this on its own, some vendors better than others. [click] So our job is two-fold: manage context on top of that, and help the agent manage its own."

---

## SLIDE 28 — Example: skills and the filesystem  (1:30 / 26:20)

"Let's make it concrete with one example: skills.

[click] A skill is literally a file on disk. [click] It has a name and a description. The LLM reads the description and decides whether to load it, like a pointer into the filesystem.

[click] Here's one: skill 'commit', description 'use when the user wants to create a git commit'. The LLM pattern-matches that description against the task.

[click] Why does this matter? Four wins.

[click] Load and unload on demand, so you only pay for context when you need it. [click] Share with colleagues, just put the skills in a repo. [click] Community skills, use what others built, like npm or pip. [click] And vendor-independent, because they're just text files.

The filesystem is your context-management layer. And you already know how to use it."

---

## SLIDE 29 — The ecosystem: different names, same idea  (1:15 / 27:35)

"And once you see this, you can't unsee it.

[click] Cursor rules: project instructions loaded into every prompt. [click] Claude Projects: persistent context across conversations. [click] GitHub Copilot instructions: repo-level context injected into the agent. [click] MCP servers: live data pulled into context on demand. [click] LangChain and LlamaIndex: frameworks that route context at scale.

[click] Some are vendor-specific, some are open. But all of them are context management.

[click] Learn the concept once, and you can apply it everywhere."

---

## SLIDE 30 — Where ideas live  (1:15 / 28:50)

"Let's zoom out.

Every idea the AI uses sits somewhere on this line. On the left, what the whole world shares. On the right, what only you know.

[click] The more common an idea is, the more likely it's already baked into the weights, for free. [click] The more specific it is to you, your team, your company, the more *you* have to hand it over.

Watch the mechanisms overlap. The weights cover the world and your industry, then fade out as you get to Cato-specific things. Skills carry the middle. Agents lean to the right, into your team's private knowledge.

Different tools, one spectrum: from the world's ideas to yours."

---

## SLIDE 31 — Putting it together: the three layers  (0:30 / 29:20)

"Quick callback. The three layers.

[click] LLM at the bottom: autocomplete at scale. [click] Agent in the middle: LLM plus tools plus a loop. [click] Context Management on top: what the LLM actually sees.

These three describe every AI product you'll use or build. Now, what do we do with them?"

---

## SLIDE 32 — Takeaways: using AI well  (2:30 / 31:50)

> Slow down. This is the payoff. Take your time.

"Three things to take home.

[click] First, Archimedes. 'Give me a lever long enough and I shall move the world.' Our version: give the LLM the right context, and it can do almost anything. The limit is the context, not the model.

[click] Second: a better agent needs *less* manual context. The best agents figure things out from minimal hand-holding. That's what you're optimizing for.

[click] And third: when AI disappoints you, ask yourself one question first. What did I forget to give it? Nine times out of ten, it's the context."

---

## SLIDE 33 — Thank you / Questions  (0:30 / 32:20)  + Q&A (~3-4 min)

"You now know the parts. Go fire the weapon.

Thank you. Happy to take questions."

> Budget ~3-4 minutes for Q&A. Likely questions and short answers:
> - **When an agent vs a plain LLM call?** When you need real-world data or multiple steps. A single fact, one call is fine.
> - **Which model is best?** Depends on the task, but the concepts here are the same across all of them.
> - **How do we use this at Cato?** Good hook for a follow-up session.

---

### Timing summary

| Section | Slides | Approx. time |
|---|---|---|
| Intro & framing | 1-6 | ~6:00 |
| Layer 1: LLM | 7-16 | ~10:20 |
| Layer 2: Agent | 17-26 | ~7:00 |
| Layer 3: Context Management | 27-30 | ~5:30 |
| Wrap-up & takeaways | 31-33 | ~3:30 |
| **Body total** | | **~32:00** |
| Q&A | | ~3-4 min |
| **Grand total** | | **~36 min** |

> Buffer tips if you're running long: slides 11-14 can each lose 15-20s by cutting
> to one example per side. Slide 27 can drop the human-intelligence analogy. The
> agent walkthrough (23-26) is the heart of the talk, protect that time.
