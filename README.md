# DRF Membership-based Social Media Web Service
Membership-based social media is an open-source platform for building membership-driven social networks — combining the features of social media with subscription-based access and content gating. The goal is to empower creators, communities, or organizations to monetize, manage, and deliver exclusive content or experiences to members.


# Simple web client for the membership-based backend service:
https://github.com/MohammadShapouri/membership-based_social_media_front-end



## Features
* User registration, login, logout, and authentication
* User profiles (with profile picture)
* Membership tiers / subscription plans
* Subscription management (upgrade, downgrade, cancel)
* Content creation: posts, media uploads (images, videos)
* Content visibility control (gated content by membership level)
* Follow / unfollow relationships
* Dashboard for creators
* API endpoints (REST) for accessing resources
* Pagination, feeds (e.g. home feed, trending, friends)
* Media storage & serving (handling file uploads, media URLs)
* Security & permissions (ensuring only permitted users see gated content)
* Settings for account (change email, password, profile settings)




## Installation
__If you use windows, instead of using '_python3 -m_' and '_python3_', use '_python -m_' and _python_' in commands.__
* Run the following command in your terminal to clone this project or download it directly.
    ```
    $ git@github.com:MohammadShapouri/membership-based_social_media.git
    ```
* Install PostgreSQL.

* Navigate to the project folder (DRF-UserAccount folder).

* Create a .env file and fill it. (.env.sample is a sample file that shows which fields the .env file have.)

* Run the following command to create virtualenv. (If you haven't installed virtualenv package, you need to install virtualenv package first).
    ```
    $ python3 -m virtualenv venv
    ```

* Activate virtualenv.
    > Run the following command in Linux
    ```
    $ source venv/bin/activate
    ```
    > Run the following command in windows
    ```
    $ venv/Scripts/activate
    ```


* Run the following command to install the required frameworks and packages.
    ```
    $ pip install -r requirements.txt
    ```

* Navigate to the config folder.

* Run the following commands one by one to run the project.
    ```
    $ python3 manage.py makemigrations
    $ python3 manage.py migrate
    $ python3 manage.py runserver
    ```



# Things to do in the future
Many parts of this project are still under development and not yet fully implemented, as I’m currently working on it alongside other commitments.
I would be glad to welcome contributions — whether it’s implementing missing features, improving existing code, or adding documentation.
## Important Features to Be Implemented
* Subscription status checking using Celery (periodic background tasks)
* Caching layer using Redis, if needed for performance
* Comment system with nested replies and moderation
* Likes / reactions system for posts and comments
