# SMHW_Wrapper

An API Wrapper for Show My Homework made in Python. Based on [@SamPoulton's Wrapper](https://github.com/SamPoulton/smhw-python), but with major fixes and changes.

---

## Changelog

---

### v0.2.0

- Added `Homework` class

- Added `HomeworkNotFound` exception

- Added `NoAuthAPI.get_homework(id)` - Returns a `Homework` when given a `Homework id`

- Removed unused `NotStoredError`

- Removed `debug` stuff

- Actually fixed token refreshing

- Fixed `User` class (logging in)

---

### v0.1.0

- Fixed Token Refreshing

- Major overhaul of `School` class
  - Fixed link getting
  - Removed API requests

- Added `NoAuthAPI` class
  - Replaces API requests in `School`