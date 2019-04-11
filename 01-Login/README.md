# Auth0 Python Web App Sample

This sample demonstrates how to add authentication to a Python web app using Auth0, and all the Auth0 Managemenet API to list rules and map them to the application they apply to.

# Running the App

To run the sample, make sure you have `python` and `pip` installed.

## Creating Auth0 Application

1. Login [Auth0](https://auth0.com) with your account, create a new Application, with the name of `demo_app`, and type of `Regular Web Applications`.
2. In the Application's `Settings`, register `http://localhost:3000/callback` as `Allowed Callback URLs` and `http://localhost:3000` as `Allowed Logout URLs`.

## Creating Auth0 Rules for whitelist

1. Login [Auth0](https://auth0.com) with your account, create a new Rule, with the name of `demo_rule`, and select the `empty rule` template.
2. Copy the script in `auth0_rule.js` file to the rule's script, and replace `NameOfTheAppWithWhiteList` with `demo_app`.
3. Add the email address you want to whitelist in the `whitelist` array.

## Setup the Python web server

1. Clone the repository to your local machine.
2. Rename `.env.example` to `.env` and populate it with the client ID, domain, secret, callback URL and leave audience blank.
3. Run `pip install -r requirements.txt` to install the dependencies and run `python server.py`. 
4. The app will be served at [http://localhost:3000/](http://localhost:3000/).


## What is Auth0?

Auth0 helps you to:

* Add authentication with [multiple authentication sources](https://auth0.com/docs/identityproviders),
either social like **Google, Facebook, Microsoft Account, LinkedIn, GitHub, Twitter, Box, Salesforce, among others**,or 
enterprise identity systems like **Windows Azure AD, Google Apps, Active Directory, ADFS or any SAML Identity Provider**.
* Add authentication through more traditional **[username/password databases](https://docs.auth0.com/mysql-connection-tutorial)**.
* Add support for **[linking different user accounts](https://auth0.com/docs/link-accounts)** with the same user.
* Support for generating signed [JSON Web Tokens](https://auth0.com/docs/jwt) to call your APIs and
**flow the user identity** securely.
* Analytics of how, when and where users are logging in.
* Pull data from other sources and add it to the user profile, through [JavaScript rules](https://auth0.com/docs/rules).

## Create a free account in Auth0

1. Go to [Auth0](https://auth0.com) and click Sign Up.
2. Use Google, GitHub or Microsoft Account to login.

## Issue Reporting

If you have found a bug or if you have a feature request, please report them at this repository issues section.
Please do not report security vulnerabilities on the public GitHub issue tracker. 
The [Responsible Disclosure Program](https://auth0.com/whitehat) details the procedure for disclosing security issues.

## Author

[Auth0](https://auth0.com)

## License

This project is licensed under the MIT license. See the [LICENSE](LICENCE) file for more info.

