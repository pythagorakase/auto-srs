# Courses

This directory holds your course-specific source material and bespoke build scripts.

**Contents are gitignored by default** (`courses/*/` matches all subdirectories) so you can drop study materials, slides, PDFs, and per-course build scripts in here without polluting the repo.

## Suggested per-course layout

```
courses/
└── YOUR_COURSE/
    ├── (PDFs, slide decks, lecture notes, etc.)
    └── scripts/
        └── build_<module>.py   # course-specific deck builder
                                # — imports from ../../../anki-deck-author/scripts/build_deck.py
```

The script in each course folder is your *application* of the skill's reusable infrastructure to that specific content. As patterns recur across multiple courses, lift the generic version into the top-level `scripts/` directory (which IS tracked).

## Why courses are gitignored

Course material is usually:
- Personal / academic content the user doesn't want in a public repo
- Copyrighted (textbook PDFs, slide decks)
- Specific to one student's context

The repo carries the **method** (the skill, the conventions, the build infrastructure). Each user brings their own course material to it.
