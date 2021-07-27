# CRM

CRM stands for Customer Relationship Management.

While looking for a project, you would probably have multiple project leads and companies,
with which you may have possibly negotiated different conditions. Keeping this information in mind can be a really big
deal. Besides that asking a client or an HR manager to remind you the hourly rate might be also quite embarrassing.

Freeturn offers lead tracking functionality, per lead CV generation for maximizing the impact, invoice generation
and a couple of other nifty features too.

!!! note
    CRM is a part of the Wagtail admin interface and can be accessed at `/admin`

## Tracking project leads

Project lead is the core element of the CRM. Go to CRM -> Projects to list all the projects you've created. Here you can
see the projects with their statuses, last activity and managers, filter on manager.

![Screenshot](img/crm/project_listing.png)

Click the inspect button to see all the necessary information about the project in detail.

![Screenshot](img/crm/project_inspect.png)

Project detail page shows the company and manager information, project status, location, duration and others plus the
the budget calculations for this project.

Adding a project is pretty straightforward:

![Screenshot](img/crm/project_adding.gif)

**Original description** would be later used for parsing the meta information about the project, technologies are fuzzy
matched if [Technology](portfolio.md#technologies) snippet.

**Project page** is a link between a project lead and a [project page](portfolio.md#project-page).

After adding a project you will be redirected to the CV generation for this project, already prefilled from your settings
and rearranged to correspond the project description, so the most relevant projects are highlighted in the CV.

### Project states and sending emails

Project leads go through the different states, representing the stages of the project acquisition.
Here are the possible project lead states and transitions:

![Screenshot](img/crm/project_state_graph.png)

Click the transition buttons from the list or inspect view of the project lead:

![Screenshot](img/crm/project_state_buttons.png)
![Screenshot](img/crm/project_state_buttons_inspect.png)

Use the intermediate state transition view to notify the project manager about the state change.

![Screenshot](img/crm/project_state_transition_view.png)

The text input field is prefilled with the template text associated with the state change. Those
templates can be configured in in Settings -> Message Templates.
![Screenshot](img/crm/message_template_edit_view.png)

Text field supports formatting, which then will be used in the emails you send to the manager of the project.
Every template will be associated with the project state transition and language the project description is in.
If no association is possible, the text field of the transition view will remain empty.

Choose the CV you would like to send to the manager along with your message.
The project's CV will be attached automatically if 'Attach CV' flag was set on the message template.

![Screenshot](img/crm/project_state_transition_buttons.png)

Click 'Send message' to send message and change the project's state or 'Just change state' to just change the state and
not send the message.

## CVs

CV and project portfolio docs are your main tool to convince the client of yourself. Freeturn is built to make every
application individual and unique, highlighting the relevant experience and skills you have, ensuring the best performance
of your application.

Go to CRM -> CVs to get the listing of your CVs.

![Screenshot](img/crm/cv_listing.png)

Click add CV to create a new CV. Mostly the CVs will be added automatically while adding a project, but nothing prevents
you from creating a new one. CVs are usually associated with a particular project, but you can also create a CV without it.

![Screenshot](img/crm/cv_adding.png)

The form is prefilled with the data from CV generation settings and your profile, so you don't need to type
them in every time.

![Screenshot](img/crm/cv_generation_settings.png)

Click inspect button to see and download the CV you've just created in PDF format:

![Screenshot](img/crm/cv_front_page.png)

1. name
1. title
1. recent projects - is the list of your projects, which match the project technologies parsed from the project
description. Can be edited.
1. skills list, skills relevant for this project are highlighted.
1. education
1. side panel including your pay rate, next available date (calculated automatically upon creation), contact data,
languages and working permit.

After the front page, which is your brief CV, follow the pages of your project portfolio.

![Screenshot](img/crm/cv_portfolio_project_page.png)

Those are exactly the data from your [portfolio site](portfolio.md#project-page), representing the information as a document.

Once your CV is created, it would probably need some polishing and customization:

![Screenshot](img/crm/cv_editing.png)

 - **relevant project pages** are the projects shown at the front page of your CV, the one matching the project's technologies
 best.
 - uncheck **include portfolio**, if you don't want to include your project listing in that document.
 - **relevant skills** is the list of technologies you want to be highlighted the cv

## Generating invoices

When the work is done, it's time to pay, and you might need an invoice for it. Freeturn offers invoice generation
functionality.

Go to CRM -> Invoices to list all your invoices. Here you can see the basic information and payment status of your
invoices.

![Screenshot](img/crm/invoice_listing.png)

Click "add invoice" to create an invoice.

![Screenshot](img/crm/invoice_adding.png)

Like CV the form is prefilled from invoice generation settings
![Screenshot](img/crm/invoice_generation_settings.png)

Usually you would associate an invoice with a project and a company, if you leave the payment data empty, they will be
automatically filled from the company's payment data. Go to CRM -> Companies, and click "edit" button at the company's
line, you want to alter the payment data for:

![Screenshot](img/crm/company_edit.png)

- **invoice number** is autoincremental and will be generated automatically.
- invoices can be created in different language. English and German are currently supported.
- **positions** are listed as a wagtail table block, click the + to add more rows
- check **payed** when the money arrives at your account

Sometimes you need to create a series of invoices, repeating the majority of the data of the previous invoice. In order
to copy the invoice, navigate to the invoice list, pick the one you want to copy, and click the copy data. The form will
be prefilled with the data from the original invoice.

![Screenshot](img/crm/cv_copy.gif)

Once the data is filled, you can inspect and download the pdf document. In order to do that, navigate to the invoice list,
pick the invoice and click the inspect button. Now you can review and download the invoice in PDF format.

![Screenshot](img/crm/invoice_preview.png)

## Messages

Mostly the project inquiries are made over email, and those can be many. An annoying routine of copypasting the project
description can be overcome with Freeturn's gmail integration.

!!! warning
    Make sure your [google oauth2 integration](configuration.md#google-oauth2) is activated

Navigate to your account settings, click "google login" button and log in to your google account.

![Screenshot](img/activating_google_account.png)

All emails labeled with "CRM" tag will be loaded and processed.

!!! warning
    Make sure your [email checker is set up](configuration.md#setting-up-mail-checker)

Navigate to CRM->Messages to see the messages loaded from your gmail account.
Text of the emails will be used to generate the projects, which you can find in the [project list](#tracking-project-leads).
Besides that Freeturn will generate a company and contact entry for the author of the email.

!!! note
    You can find all your companies at CRM -> Company and contacts at CRM -> People
