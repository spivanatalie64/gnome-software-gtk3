# GTK3 Port Project Plan

Date: $(date --iso-8601=seconds)

Overview:
- Goal: Port gnome-software to GTK3 with minimal, surgical changes.

Team:
- PM: pm-agent
- Engineers: senior-eng-01 .. senior-eng-50

Initial assignment mapping (task -> primary branch):
- Task 1: gtk3-task-1-01 (Update build files for GTK3)
- Task 2: gtk3-task-2-01 (Adwaita compatibility layer)
- Task 3: gtk3-task-3-01 (Migrate CSS to GTK3)
- Task 4: gtk3-task-4-01 (Convert UI files to GTK3 format)
- Task 5: gtk3-task-5-01 (Update widget code for GTK3 APIs)
- Task 6: gtk3-task-6-01 (Adjust signal/connect usage)
- Task 7: gtk3-task-7-01 (Fix header includes and types)
- Task 8: gtk3-task-8-01 (Update gs-shell and application init)
- Task 9: gtk3-task-9-01 (Update custom widgets)
- Task 10: gtk3-task-10-01 (Update list/row widgets)
- Task 11: gtk3-task-11-01 (Screenshot carousel & image handling)
- Task 12: gtk3-task-12-01 (Port dialogs)
- Task 13: gtk3-task-13-01 (OS update / upgrade banner)
- Task 14: gtk3-task-14-01 (Update plugin bindings)
- Task 15: gtk3-task-15-01 (Translations and po updates)
- Task 16: gtk3-task-16-01 (Update help/metainfo and desktop files)
- Task 17: gtk3-task-17-01 (Update unit/integration tests)
- Task 18: gtk3-task-18-01 (Accessibility checks)
- Task 19: gtk3-task-19-01 (Runtime warnings and leak fixes)
- Task 20: gtk3-task-20-01 (Update README & BUILD docs)

Schedule (high level):
- Week 1: Project setup, build matrix, PM plan, spawn engineers, start Task 1-5
- Week 2-4: Implement GTK3 port features, split tasks across engineers
- Ongoing: CI, tests, review, merge per-task PRs

Acceptance criteria: see task mapping and per-task criteria in repo issue tracker or this plan.

