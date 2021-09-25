# Beagle Logs

## Meeting Minutes #1

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

Date: - *25/09/21*
Participants: All members
Duration: 35 Minutes

### Objectives

- Establishing More Meetings
- Task Delegation
-- Considering a Different Approach to Delegating Tasks
-- Tasks
- Refactoring Current Implementation
-- Accessing data in a standardised way
-- Changes in Git Etiquette
-- Fixing Style and Documentation

## Meeting details

### Establishing More Meetings
 Heeding Hayden's advice, we decided to begin having meetings about 3-4 times a week. 
- These meetings will resemble standups, where each team member will take about a minute to describe what they have been working on, what they will work on and any obstacles that they are facing at the moment.
- Not every team member will  be required to turn up at all of these meetings.

## Task Delegation
### Considering a Different Approach to Delegating Tasks
 Dhruv brought up the idea of using the Agile methodology in future implementations, which had been brought up during the lectures. 
- We collectively decided that we did not need to immediately begin using this methodology as we know each other quite well, and most issues have already been effectively communicated with each other.
- However we are still taking this into consideration for the second implementation.

### Tasks
The tasks were delegated as follows:
| Task    | Person(s)    |
|---------|-----------|
| New functions | Dhruv & Christian|
| Rewrite tests | Sam & Sarah |
| Create fixtures | Lawrence |
| Implement access error for auth_user_id_ which checks for invalid user ID | Sam |
- New Functions
-- This task involves creating the new functions that will directly change the database. These functions will be in a seperate file from the current functions. 
-- The current functions will also be changed to integrate the functions that directly change the database. 
- Rewrite tests
-- With the creation of the new functions, new tests will need to be written to check the integrity of both the new and old functions.
- Create fixtures
-- Create fixtures for the current implementation.
- Implement access error for auth_user_id_ which checks for invalid user ID
-- Currently, the function auth_user_id lacks testing for invalid user ID. An access error should be produced when an invalid user ID is detected. 

## Refactoring Current Implementation
### Accessing data in a standardised way
After our tutorial, we received insightful feedback regarding our current implementation. The biggest issue raised was regarding the lack of standardisation in our code. 
- Currently, our functions directly writes into the database, which is not desirable.
- We need to refactor our functions by creating other functions that will receive information and then change the database. 
-- This will reduce data modification
-- More abstract way of coding may be beneficial in future implementations.

We discussed in more detail how this will look like:
- A new file will be created, containing the only functions that will directly change the database
- Functions that this file will contain will be:
-- create_user
-- get_user
-- update_user
-- remove_user

These changes will require us to change all of out current functions, and hence, new tests as well. 

### Changes in Git Etiquette
Dhruv pointed out that we should stop approving our pull requests and having another teammate to merge our request. Instead, we should do the opposite where others will approve our own request and we then merge the request. 
- This creates accountability and some sort of safety net in case an undesirable pull request is approved.

### Fixing Style and Documentation
We realised that we needed to improve our styling, including making descriptions of functions that we have made.
-   To aid us in this, we have decided to start using pylint as a way to identify these mistakes.
