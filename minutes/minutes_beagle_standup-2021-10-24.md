# Beagle Logs
## Meeting Minutes #5
[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)
Date: - *24/10/21*
Participants: All members
Duration: 60 Minutes
### Objectives
- Going over spec to maximise marks
- Writing Doc-strings for new functions
- Test Styling
- Plans for iteration 3
## Meeting details
### Going over spec to maximise marks
Upon commencing one of our very frequent meetings, Dhruv quickly established the very unfortunate fact that our group had dropped from 10th to 14th place, due to the recent slight inactivity of some of our group members. 
- Over the 3 leaderboards, we realised we were capped at around the 95 mark, seeing as our program had failed some of the 1531 Pytests. We decided to go thoroughly over the spec to find out what we were missing to maximise our marks. Whilst it may be unlikely to get 100 on iteration 2, it was worth a shot/
## Doc- Strings
Despite our leaderboard position not being optimal, and removed from the top 10, we still had to work on the styling and Doc-Strings to keep our code documentation as clean as it was in iteration 1. The task delegation is as follows.
### Task Delegation
| Task                                   | Person(s)         |
|----------------------------------------|-------------------|
| Thoroughly go over spec and fix bugs   | Dhruv & Christian |
| Write doc strings for new functions    | Sam               |
| Consistency in code styling            | Lawrence          |
- Thoroughly go over spec and fix bugs
-- Dhruv and Christian went over the spec to ensure that no bugs were missed. We paid careful attention to dual errors for Access and Input errors.
-- We also need to make sure that we are not importing functions that we are not allowed to use (those that are not in the current specification). 
-- Dhruv and Christian have both agreed to do pair programming, which has worked great in the past
- Fix bugs with our edit message

## Frontend testing
Testing on the frontend was very important as it allowed us to discover several missing features in our implementation.This involved our message edit function duplicating messages that were being added, as editing a message had added it into our datastore
-- Most of the implementation has been done as well as tests. 

## Coverage
Upon fixing our coverage we discovered that a helper function check auth user exists, which we created in Iteration 1, was redundant and not doing anything
