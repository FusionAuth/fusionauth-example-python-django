# secret-birthdays

This application will let users put in their birthdays and keep this “secret”
information safe for them. With these basics in place, you’ll
see how FusionAuth works and how it can extend the application
to do whatever you need. The application will also let users sign-in
using their google account.
You can read the detailed blog post here: https://fusionauth.io/blog/2020/07/14/django-and-oauth/ 

## Prerequisites

You need to make sure FusionAuth is running and that you have python3/pip3 available. 

## Setup

*  `virtualenv sb-env`
*  `source sb-env/bin/activate`
*  `pip3 install django dateparser fusionauth-client pkce`
*  `django-admin startproject secretbirthdays`
*  `cd secretbirthdays`
*  `python3 manage.py startapp secretbirthdaysapp`
*  `python3 manage.py makemigrations`
*  `python3 manage.py migrate`
*  `python3 manage.py runserver`

## Running 

To run this: `python3 manage.py runserver`

# Credits

* [@sixhobbits](https://github.com/sixhobbits) from [https://ritza.co](https://ritza.co) for the initial implementation.
