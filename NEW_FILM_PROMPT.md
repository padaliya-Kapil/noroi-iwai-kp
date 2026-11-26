I want to make a new short animated film, drawn, animated and scored entirely in code, in the GitHub repository padaliya-kapil/noroi-iwai-kp.

## Start here
- Create a new branch called `[BRANCH NAME, e.g. film-2]` from the branch `ikaros-film`. Do not change `main` or `ikaros-film`.
- Read `ikaros/README.md` and the code in `ikaros/` first. It is a finished 2-minute collage film of the Icarus myth, and its toolkit is what you should reuse:
  - `collage.py`: torn and cut paper, paper textures, engraving and halftone prints, gold leaf, shadows, a camera over larger pages, hand-placed stop-motion jitter
  - `figure.py`: jointed paper puppets with poses, turning heads, costumes, wings
  - `shotkit.py`: shared scene pieces, time-of-day lighting grades (dawn to sunset)
  - `letters.py` and `shots/card.py`: a cut-paper alphabet and silent-film title cards
  - `music.py`: synthesized instruments, sound effects timed from the shots, and the mix
  - `render.py`: parallel rendering, contact-sheet previews, final assembly
- Put the new film in its own folder (for example `film2/`), copying and adapting what it needs from `ikaros/`, so the Icarus film keeps working.

## The film
- Story: [YOUR STORY, as a list of moments, one line each]
- Look and style: [e.g. paper collage / shadow puppets / woodcut / flat graphic; colours; any references]
- Length: [e.g. about 60 to 90 seconds]
- Sound: [instrumental only / which instruments or mood]
- Text on screen: [none / silent-film title cards between scenes / a title only]

## Rules
- Everything is made in code: no image files, no found or downloaded images, no fonts on screen (letters are drawn as strokes), no audio samples, no AI image or video generators.
- 1920x1080, 24 fps, drawn on twos (12 drawings a second), shots timed to the music's tempo.

## How we work (please follow this order and wait for my notes at each step)
1. Write the story as a shot list and timeline. Show it to me before building.
2. Make one style-test still. I approve the look before anything moves.
3. Make a 3-second motion test. I approve the motion.
4. Build the film shot by shot. Check every shot with contact sheets before rendering, and look closely at figures, hands, feet and anything that might read as unclear.
5. Compose the score and sound effects, timed from the shots. Measure the mix with loudness numbers and a spectrogram, and tell me what I should listen for, since you can't hear it.
6. Render, assemble and send me the video, then take my notes and fix them.

Things I learned last time:
- Make sure each scene's story is clear to someone who doesn't know it. Show why things happen, not only what happens.
- Keep the light changing with the story (time of day), so the sky never feels static.
- Keep characters at consistent sizes from shot to shot, and keep figures from overlapping.

## Saving
- Commit and push to `[BRANCH NAME]` as you go.
- Commit the finished video as a regular file under 100 MB (two-pass encode to about 95 MB). Git LFS does not work, because this repository is a public fork.
- Also send me the full-quality master file directly so I can download it.
