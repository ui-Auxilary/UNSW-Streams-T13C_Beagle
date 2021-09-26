# Beagle Logs

## Standup #1

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

Date: - *26/09/21*
Participants: Dhruv, Lawrence, Christian
Duration: 15 minutes 

### Objectives

- Discuss AGILE methodology
- Explain the usefulness of a standup
- Progress Update and next steps

---
## Standup details

Dhruv began by breifly explaining what the AGILE methodology and standups asynchronous/synchronous were.

### AGILE methodology

- The AGILE methodology endorses the four **key values** of:
> Individuals and interactions over processes and tools

> Working software over comprehensive documentation

> Customer collaboration over contract negotiation

> Responding to change over following a plan

**Highlighted point**
>The AGILE method helps us realise a more dynamic way to work with people, focusing on the available people rather than the tools. By pair programming, we are constantly looking at other people's codes rather than to make a perfect system with tools. As documentation is something that constantly changes as the program advances, we shift the focus to developing working software than a rigid documentation which will be quickly outdated. We must take the client's best interest into mind, engaging in a constant dialogue with the stakeholders and finally adaptable to any situation thrown at as, rather than stick to a solid plan since reality doesn't work like that.  

> It's important to be adaptable and ready to respond. ie. There could be sudden changes in iteration 2 and 3, requiring us to make a huge alteration in our work

### Standups
> Asynchronous standups do not need to involve all members, but generally standups are short meetings

**3 Key questions**:
-   What did I do?
-   What problems did I face?
-   What am I going to do?


**Highlighted point**
> Standups are good because they let us set realistic goals with the people we have, and they're short but detail us on our progress individuallly and as a group. This helps us envision a scope of our timeline and when we can get things up and ready.
---
### Progress Update
**Christian**
- What did he do?
Taking in feedback from the tutor, Christian worked on standardising the method of manipulating the datavase via.the data_operations.py file which introduces a set of standardised functions that update and modify the data_store as necessary. Christian and Dhruv pair-programmed and implemented test files first, before starting on the implementation of those operations. Previously individual functions ie. auth.py and channels.py had functions that accessed the database, which would prove to be an inconvenience if the data_store or method of storing data had changed in the near future. Together, they created a standardised method of handling data, and accessing the data instigating the following functions:
---
''
ADD_USER
    - Adds a user to the database

GET_USER
    - Retrieves a user from the database

GET_USER_HANDLES
    - Retrieves a user's handle from the database

GET_USER_EMAILS
    - Retrieves a user's email from the database

ADD_CHANNEL
    - Adds a channel to the database

GET_CHANNEL
    - Retrieves a channel from the database
''

- Problems he faced

Whilst the implementation of the data_operations is correct, a big refactor must be made to the main code ie. auth.py and channels.py to ensure they are using the new standardised functions.
- What will he do:

Assign this task to Sarah and Samantha, to both refactor the old functions and update any tests which will be affected by this change.

**Lawrence**
- What did he do?

Lawrence explained his understanding of fixtures to us
> If there are repeated lines of code in our tests we can use fixtures, to simplify the tests and make it more readable, by reusing code rather than copying over the same thing several times.
- What problems did he face?

Lawrence had trouble deciding what to change to fixtures, and couldn't make a start until the functions were refactored by Sarah and Samantha
- What will he do?

Take a look through our old code, wait until the refactors have been implemented and in the meantime, preemptively plan what he could possibly convert to fixtures.

## Task Delegation

Updates, we made use of the board in GitLab:
![Boards.PNG](https://www.dropbox.com/s/ef1dzh3p8shbe4l/Boards.PNG?dl=0&raw=1)
The tasks were UPDATED as follows:
- Sarah and Samantha will update auth_login_1 and auth_register_v1 and other files
which involve directly modifying the database
- Lawrence will update fixtures, and add some code documentation
- Dhruv will do channel_details_v1
- Samantha will channel_messages_v1 and add global error handlers