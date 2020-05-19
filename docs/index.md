# Getting started

Freeturn is an open source portfolio and CRM for individual freelance developers.
Based on Django and Wagtail.

## Features

### Portfolio

![Front page](https://cheparev-portfolio.s3.amazonaws.com/images/Selection_069.original.png)

* minimalistic front page including picture and online identity
* portfolio project pages with all necessary info
* contact form
* [more ->](portfolio.md)
### CV generation

![Screenshot](img/crm/cv_front_page.png)

* quick per project CV generation using your project portfolio proven working against HR managers
* Gmail integration, parsing the project description for quick project lead and CV generation
* [more ->](crm.md#cvs)

###  CRM

![CRM area](https://cheparev-portfolio.s3.amazonaws.com/images/Office_-_Projects_070.original.png)

* tracking project leads and budgeting
* clients database
* invoice generation
* [more ->](crm.md)

## Deployment

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/eviltnan/freeturn/tree/develop)
or check out freeturn [locally](contribution.md) for development and contribution

Freeturn ->

- thankfully uses Circle CI for CI/CD: [![eviltnan](https://circleci.com/gh/eviltnan/freeturn.svg?style=shield)](https://app.circleci.com/pipelines/github/eviltnan/freeturn)
- is MIT licensed: [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
- thankfully uses end-to-end-tests on browserstack and selenium: [![BrowserStack Status](https://automate.browserstack.com/badge.svg?badge_key=OW9FSlpEWUdYb2htbFJYTjRPbEtUVmlNRUhZM2RCNVUwejZ5MzAxUTJLMD0tLUcySUFHVGJVMDdVNzZxZ3VGSTdhSEE9PQ==--2fb0726c5380e49390677a7fdb8e19a5903d2828)](https://automate.browserstack.com/public-build/OW9FSlpEWUdYb2htbFJYTjRPbEtUVmlNRUhZM2RCNVUwejZ5MzAxUTJLMD0tLUcySUFHVGJVMDdVNzZxZ3VGSTdhSEE9PQ==--2fb0726c5380e49390677a7fdb8e19a5903d2828)
- thankfully tracks maintainability with code climate: [![Maintainability](https://api.codeclimate.com/v1/badges/4aa9a9a8ce0e799208d4/maintainability)](https://codeclimate.com/github/eviltnan/freeturn/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/4aa9a9a8ce0e799208d4/test_coverage)](https://codeclimate.com/github/eviltnan/freeturn/test_coverage)

## Configuration

Freeturn supports a number of service integrations, [configurable over environment variables](configuration.md).
