# Beagle Logs

## Meeting Minutes #3

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

Date: - *30/09/21*
Participants: All members
Duration: 60 Minutes

### Objectives

- Climbing the leaderboard
- Kind of Cringe
-- Task Delegation
- Coverage

## Meeting details

### Climbing the Leaderboard
Upon commencing one of our very frequent meetings, Dhruv quickly established the very unfortunate fact that our group had dropped from 10th to 14th place, due to the recent slight inactivity of some of our group members. 
- We take leadership and being the best programmers very seriously. Thus, we decided to take back our rightful place in top 10 by grinding on this project together with a 5-way programming pair.

## Kind of Cringe
Despite our leaderboard position being kind of cringe, we realised there were other issues that also had to be addressed. 

### Task Delegation
| Task                                   | Person(s)         |
|----------------------------------------|-------------------|
| Redo tests and clean up code           | Dhruv & Christian |
| Finish channel_messages implementation | Sam               |
| Create doc.strings                     | Lawrence & Sarah  |

- Redo tests and clean up code
-- Currently our tests have a mix of black box and white box testing. We need to get rid of all white box testing, even if it means leaving some functions not tested fully. This is due to the lack of specs given in the current iteration. 
-- We also need to make sure that we are not importing functions that we are not allowed to use (those that are not in the current specification). 
-- Dhruv and Christian have both agreed to do pair programming, which has worked great in the past
- Finish channel_messages implementation
-- Most of the implementation has been done as well as tests. 
-- Since testing the entire function requires using features such as sending messages and viewing messages which have not been released in this iteration, this function is unable to be fully tested.
- Create doc.strings
-- doc.strings is a documentation file which consists of all the functions created in this project. 
-- Each documented function will have a short description of its purpose, arguments, errors, and return values.

## Coverage
With some limitations such as not having access to full specifications, we aim for 100% coverage accross all our files.
