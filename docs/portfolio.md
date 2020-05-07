# Portfolio

Besides the obvious pieces on your freelance web identity like popular professional networks, the hiring companies and
client would want to see your personal and unique portfolio website. Freeturn offers a quickly configurable yet
sufficient way to build the summary presentation of your experience and project portfolio.

Please make sure you at least briefly read the [wagtail's editor's guide](https://docs.wagtail.io/en/latest/editor_manual/index.html),
so you understand the basic concepts of editing content with Wagtail CRM.

## Home

![Screenshot](img/home.png)

This is the landing page the visitors of your homepage will be seeing at first. Most of the fields are pretty much self
explanatory, yet some elements are calculated on the fly using the data about your current projects.

1. **title**: put your name, like "Mary Poppins"
1. **claim**: put your claim here "Freelance baby sitter"
1. **social links block**: configure your web identity here. Github, stackoverflow and linkedin are currently supported.
1. **earliest available block**: the next date you accept offers. If left empty, then the next free month beginning is
automatically calculated, so your profile looks up to date.
1. **speed links**: speed links are calling the user to action. *Current project* leads to the [last project](#project-page)
in your project portfolio, *to porfolio* encourages visitors to familiarize themselves with your [project list](#projects-listing) and
*request CV* leads directly to the [contact form](#contact-form).
1. **picture**: pick the one you think suits best.


Besides that you can configure the color of title and don't forget about the promotion options coming with Wagtail out
of the box. Page title will be used by the search engines to represent your page in the search results, and you would
probably want it to look pretty.

## Projects listing

![Screenshot](img/portfolio.png)

Project listing represents the summary view on your projects. The entries are briefly showing project pages,
letting the visitors to get an overall picture of your skills.

There is not much you can customize about it, besides the page title (1) and the summary (2) for each project at the
project page editing view.

## Project page

![Screenshot](img/project_page.png)

Project page represents a particular project to the visitor. This data is also reused in the [CV generation](crm.md#cvs).

1. **title**: the title of the project, as you wish it to be shown in the list and at the title of the page
1. **start and duration**: specify the start and the end date of the project, the length is calculated
1. **position**: your position at that project
1. **responsibilities**: your responsibilities at the project. Those are defined as [Wagtail snippets](https://docs.wagtail.io/en/latest/editor_manual/documents_images_snippets/snippets.html)
1. **link**: link to your project, for showcasing your work
1. **technologies**: an important piece of information, also implemented with snippets.
Technologies will be used for [CV generation](crm.md#cvs). Clicking on technologies leads to the portfolio view, showing
only projects using this technology and also a brief description, which you specify while adding a technology
![Screenshot](img/portfolio_filtered.png)
![Screenshot](img/add_technology.png)
1. **project description**: rich text field, where you can put the exhaustive description of your project.
1. **back to portfolio**: the button to get to the overview of the projects.

## Contact form
