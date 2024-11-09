# This is the kicassoo store readme

## unsolved bugs

- nav bar dropdown on screen sizes below 332px is a pain in the ass as it the dropdown does not ocnnedct to the nav bar making it look not great

- homepage styling on screens below 450px the buttons go out of the image this may be to do with my cody and home-content heigh calculations??


## Notes

- to import products from store use terminal command "python manage.py import_products"

- in checkout to create Draft/test order set "confirm" to false in services.py line 48 and views.py line 30

- Details and category need to be added manually to the imported products


- checkout is very robust it stores the order as soon as a person enters their card details with a status of payment pending then the webhook carries the order number on receipt of a succesful payment webhook the order payment status is updated to completed and the order is sent to printful via the API.. I did originally put all of the order info onto the webhook but this caused problems due to the 500 characther limit the stripe webhook is restricted to. Another great benefit of the way that checkout is setup is that If a user's payment fails and they do not choose to use another card and complete the order, You will have the order stored with a payment failed staus from here you can aquire the user's information  such as email address and send them reminders or discount  to encourage completion of order.

- mention the webhook error in solved bugs, I had a problem when there were many items(over 4 or 5) on an order i got an error due to the stripe webhook having a character limit of 500, I had set the webhook up to contain all of the order data including the items but this is what was causing the error. To solve the issue I implemented that as soon as the user submits their card details the order is created with a payment pending status, then that allowed for the webhook to only need to hold the order number. When the webook returns a payment intent succeeded with the order number only then is the order payment status updated to completed and the order is sent to printful for fulfillment.




# [Kicassoo](https://jaycode88.github.io/Kicassoo/)


** amiresponsive image here **

Welcome to Kicassoo, the online showcase for an abstract artist's captivating collections. This website highlights Kicassoo's profile and creative works while offering visitors a glimpse into the vibrant world of contemporary art. With the addition of a dedicated Print Store, users can now explore and purchase a variety of products featuring Kicassoo's unique artwork, merging art appreciation with accessible, personalized pieces.

## Purpose
The primary purpose of the website is to establish a professional online presence for Kicassoo, an abstract artist, by showcasing curated collections and offering a unique shopping experience. Kicassoo serves as a platform to introduce the artist’s work to a broader audience, offering visitors an insight into the artist's creative vision and distinctive style.

With a focus on simplicity and elegance, the website features an accessible Print Store where visitors can purchase a variety of products adorned with Kicassoo's artwork. This addition enhances engagement by allowing art enthusiasts to bring Kicassoo’s creations into their personal spaces, further connecting them with the artist's expressive work. Through both artistic display and functional eCommerce, the site captures and celebrates the essence of Kicassoo's art, fostering a deeper connection with visitors.

## UX
### Colour Scheme
we've opted for a simple black and white color scheme. This deliberate choice is intended to create a minimalist backdrop that allows the artwork to take center stage. By keeping the overall design subdued, we aim to highlight the vibrant colors and intricate details of the artwork featured on the site.

The monochromatic palette not only emphasizes the visual impact of the images but also lends a sense of sophistication and timelessness to the website's aesthetic. Additionally, the use of black and white provides a versatile canvas that allows the artwork to shine while ensuring readability and clarity of text and navigation elements.

By embracing simplicity in our color selection, we aim to create a cohesive and elegant visual experience that puts the focus squarely on the artistry and creativity of the showcased collections.


### Typography
#### Headings

![Font](documentation/montaga.webp)

For the headings, we've chosen the "Montaga" font. This font exudes elegance and sophistication, making it the perfect choice to represent the artist's brand and to headline the various sections of the website. Its graceful curves and bold strokes command attention, while its timeless aesthetic adds a touch of refinement to the overall design.

#### Body Text

![Font](documentation/opensans.webp)

The body text is set in "Open Sans." This font was selected for its clean and modern appearance, which enhances readability across different devices and screen sizes. With its neutral yet friendly demeanor, Open Sans ensures that the content remains accessible and easy to digest, allowing visitors to focus on the artist's narrative and portfolio without distraction.


## User Stories

### As a new User ...

- I want to easily navigate the site to find collections, products, and information about the artist.
- I want to view available collections and understand the themes or inspiration behind each.
- I want to see various products featuring Kicassoo’s artwork, with clear descriptions, sizes, and pricing.
- I want to know more about the artist and the story behind their work.
- I want to contact the artist directly for inquiries or specific requests.

### As a returning user ...
- I want to be able to sort and filter products by category or type (e.g., “Wall Art” or “Stationery”).
- I want to quickly access my cart and review items before checking out.
- I want a fast, secure, and intuitive checkout process.
- I want to be able to easily connect with the artist on social media.

### As Site Owner ...

- I want a site that reflects my artistic identity and vision.
- I want to manage products, including adding new items and updating details.
- I want my artwork to be be secure from theft.
- I want an integrated checkout process that handles orders efficiently.
- I want to receive notifications of new orders and manage fulfillment through Printful.

## Wireframes

### Home

![screenshot](documentation/wirehome.webp)

### Collections

![screenshot](documentation/wirehome.webp)

### Collection Detail

![screenshot](documentation/wirecollectiondetail.webp)

## Features
### Responsiveness & Accessibility
The site has been built to be perfectly responsive accross all devices for 320px wide and up. Special care has been taken to ensure the correct size image is loaded for the correct device type ensuring lower load times and high performance. 
The site Has a 100% accessibility score, ensuring it is accesible to screen readers and other assitive technologies Therefore reaching wider audiences.

### Image Copy protection code
To deter casual attempts at image theft, right-click options on images are disabled, preventing common actions such as "Copy" or "Save image as." Although this measure doesn’t provide complete protection, it acts as a basic deterrent. Collection images are also displayed with a copyright watermark overlay to act as a further detterent.

### Navigation
A clear, accessible navigation bar enables users to easily find their way around the site. The navigation bar includes the Kicassoo logo and links to essential pages. On smaller screens, the navigation collapses into a dropdown menu for seamless access.

### Printful API Integration
This integration automates product import and order fulfillment directly through Printful, enhancing the store’s print-on-demand capabilities:

- **Product Import Command:** Products from the artist’s Printful catalog can be imported directly into the store using the command:

python manage.py import_products

This command retrieves product details, including variants, sizes, and prices, ensuring accurate catalog management.

- **Automated Order Fulfillment:** When an order is completed, it is sent to Printful through the API for fulfillment, ensuring seamless order processing from checkout to delivery.

### Stripe Payments
Stripe powers secure payment processing within the store, allowing customers to pay with ease. Stripe’s PaymentIntent API creates a secure transaction environment, and users can confirm payments within the checkout flow.

## Stripe Webhook Integration
The Stripe Webhook monitors payment success and triggers the following automated processes:

- **Order Status Update:** Upon receiving a “payment succeeded” webhook, the system updates the order status to “completed.”
- **Order Transmission to Printful:** Once payment is confirmed, the completed order is automatically sent to Printful for production and shipping.

- **Order Confirmation Email** Upon a succesfull payment the order confirmation email is sent.

- **Failed Payment Handling:** If a payment fails, the webhook marks the order as “failed,” allowing site admins to follow up as necessary.

## Page Features
### Home Page
The home page consists of A hero image, with 2 call to action buttons inviting the user to view the artist's collections or view the Print store.

### About me
The About page provides more in-depth information about the artist, displayed alongside an artist photo, offering users a personal look into the journey and inspiration behind the art.

### Collections
This page Features each of the artist's collections with a description, Image and a button to view the collection.

### Collection Gallery
Each Collection has its on gallery page to display the Art pieces from each collection, Here the user can find the Title of the art pieces. As well as a call to action contact button for the user to make enquiries, along side a view store button to invite the user to the eccom store.

### Contact form Modal
The contact form is embedded in a modal that can be accessed from any page. Using Django's email handling (connected to a Google account via an app password), the form sends user inquiries directly to the artist’s email. The form requires the user’s name, email address, and message, with built-in validation to ensure all fields are correctly completed.

![Contact Modal](documentation/contactmodal.webp)

### Product List Page
The Product List page displays the full selection of products available for purchase. Users can filter products by category and sort by price or other parameters, making it easy to browse through Kicassoo’s artwork applied to different product types, such as “Wall Art” and “Stationery.”

### Product Detail Page
Each product has a detail page where users can view available variants, select options like size, and view additional product information. Users can also adjust quantities and add items to their shopping bag from this page.

### Shopping Bag Page
The Shopping Bag page displays selected items, quantities, and subtotal costs, giving users control to adjust quantities or remove items. This page also allows users to proceed to checkout or return to shopping.

### Checkout Page
The Checkout page handles the payment and order summary, allowing users to enter delivery details, calculate shipping costs based on location, and proceed with payment using Stripe. Users see a clear breakdown of item costs, shipping, and the final total.

### Order Success Page
After a successful order, users are redirected to the Order Success page, where they receive confirmation of their purchase. Users are informed that an order confirmation email has been sent.

### Footer 
This contains social links and contact button for Kicasso as well as Socail links for the site developer.
![Desktop Footer](documentation/desktopfooter.webp)
![Mobile Footer](documentation/mobfooter.webp)


## Future features
### Pagination
As there are more products added to the store, when the number reaces 20+ it would be a good idea to instal pigination on the product list page, this will provide a better user experience over an endles page of products

### Profiles
As orders climb in quantity it would be a good to add user profiling so users can access past orders and save delivery addresses etc. This is also good for data collection.


## DEPLOYMENT
### Local Deployment
This project can be cloned or forked in order to make a local copy on your own system.

#### Cloning

You can clone this repository by following these steps:

1. Go to the [GitHub repository](https://github.com/Jaycode88/kicassoo) 
2. Locate the Code button above the list of files and click it 
3. Select if you prefer to clone using HTTPS, SSH, or GitHub CLI and click the copy button to copy the URL to your clipboard
4. Open Git Bash or Terminal
5. Change the current working directory to the one where you want the cloned directory
6. In your IDE Terminal, type the following command to clone my repository:
        - `git clone https://github.com/Jaycode88/kicassoo.git`
7. Press Enter to create your local clone.

Alternatively, if using Gitpod, you can click below to create your own workspace using this repository.

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/Jaycode88/kicassoo)

Please note that in order to directly open the project in Gitpod, you need to have the browser extension installed.
A tutorial on how to do that can be found [here](https://www.gitpod.io/docs/configure/user-settings/browser-extension)

#### Forking

By forking the GitHub Repository, we make a copy of the original repository on our GitHub account to view and/or make changes without affecting the original owner's repository.
    
You can fork this repository by using the following steps:

1. Log in to GitHub and locate the [GitHub Repository](https://github.com/Jaycode88/kicassoo)
2. At the top of the Repository (not top of page) just above the "Settings" Button on the menu, locate the "Fork" Button.
3. Once clicked, you should now have a copy of the original repository in your own GitHub account!

### Live Deployment

This section will be updated with platform-specific deployment instructions once a live hosting provider is selected.

## Tools and Technologies used
- [HTML](https://en.wikipedia.org/wiki/HTML)  is the backbone of web content. It defines the structure and content of the web pages.
- [CSS](https://en.wikipedia.org/wiki/CSS) used to control the visual presentation of the web application. It defines the layout, colors, fonts etc.
- [Git](https://git-scm.com) used for version control. (`git add`, `git commit`, `git push`)
- [GitHub](https://github.com) used for secure online code storage.
- [Font Awesome](https://fontawesome.com/) For Icons
- [Google Fonts](https://fonts.google.com/) for all Fonts.
- [Responsinator](http://www.responsinator.com/) Used to check responsiveness.
- [FormKeep](https://formkeep.com/) Used for contact form back end.


## Bugs
### Open Issues


### Solved bugs
#### Font package
I had an issue When the user hovered over a button, all the text changed to black except for the letter "N". I diagnosed this to be a font package issue as when I load the buttons with a different font the problem did not exist. The other option I found was to remove the text transform to uppercase class. 
I discussed with client which resolution they preffered and it was chosen to remove the uppercase transform.

#### Logo
I recieved an image to use as a logo but this was not of sufficient quality and did not look good on the preview site, I requested another image but this was poorly sized and pixelated.
I managed to get a much clearer image using image manipulation and AI software.


## Upon sign off

- Sign Customer upto FormKeep and transfer code so messages go to their account.
- Use customer gmail for Recaptcha security on form.
- Publish with chosen Host.