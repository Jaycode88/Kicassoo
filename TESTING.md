# developer note!
ensure orders are set to confirm for final deployement


- in checkout to create Draft/test order set "confirm" to false in services.py line 48 and views.py line 30

# Testing
Return back to the [README.md](README.md) file.

I have used various tools to Test Funcionality, Validity and responsiveness. I have been sure to check all layouts, colours, text, forms, links, buttons are functioning on all devices and screen sizes that I have tested.

## Code Validation

### HTML
All pages files have been tested with [W3C Markup Validation Service](https://validator.w3.org/) to check validation.

- Home Page - PASS
- About Page - PASS
- All Collections page - PASS
- The Kingdom page - PASS
- Ropes of Wisdom page - PASS
- Perfect Moments page - PASS
- Events page - PASS
- Product List page - PASS
- Product Detail page - PASS
- Shopping Bag page - PASS
- Checkout page - PASS
- Order Success page - PASS

### CSS

All CSS files have been tested with [W3C CSS Validator](https://jigsaw.w3.org/css-validator) to check validation.

- base.css - PASS
- home.css - PASS
- products.css - PASS
- bag.css - PASS
- checkout.css - PASS

### JavaScript

All Javascript files have been tested with [JShint Validator](https://jshint.com) to check validation. I used version 11 which does not throw errors due to use of ES6 syntax, Aswell as informing JSHint that I was intenionally using jQuery.

- sorting-script.js - PASS
- event-script.js - PASS
- copyright-script.js - PASS
- contact-modal.js - PASS
- back_to_top_script.js - PASS
- variantandquantity.js - PASS

The Javascript in the checkout.html could not be validated due to its use of Python code but a temporary structure without the use of Python was used for a successful code validation.

### Python PEP8 Compliance

All python files have been tested with [Python Linter](https://pep8ci.herokuapp.com/) (Provided by CodeInstitute) to ensure they are PEP8 compliant.

Kicasso_store:
- settings.py - PASS
- urls.py - PASS

Home App:
- views.py - PASS
- urls.py - PASS
- forms.py - PASS
- context_processors.py - PASS

Products App:
- views.py - PASS
- urls.py - PASS
- printful_service.py - PASS
- models.py - PASS
- admin.py - PASS
- import_products.py - PASS

Bag App:
- views.py- PASS
- urls.py - PASS
- contexts.py - PASS

Checkout App:
- views.py- PASS
- urls.py - PASS
- services.py - PASS
- models.py - PASS
- forms.py - PASS
- admin.py - PASS
- email.py - PASS

## Bugs
### Open Issues
none currently listed

### Solved bugs
#### Stripe Webhook
When first testing the Stripe webhook I found that if an order had too many items in it the order process would fail due to the stripe webhook having a character limit of 500, I had set the webhook up to contain all of the order data including the items but this is what was causing the error.

To solve the issue I implemented that as soon as the user submits their card details the order is created with a payment pending status, then that allowed for the webhook to only need to hold the order number. When the webook returns a payment intent succeeded with the order number only then is the order payment status updated to completed and the order is sent to printful for fulfillment.

This feature includes a bonus in that the site admin can see orders that have not completed payment and follow them up with an email.


#### Font package
I had an issue When the user hovered over a button, all the text changed to black except for the letter "N". I diagnosed this to be a font package issue as when I load the buttons with a different font the problem did not exist. The other option I found was to remove the text transform to uppercase class. 
I discussed with client which resolution they preffered and it was chosen to remove the uppercase transform.

#### Logo
I recieved an image to use as a logo but this was not of sufficient quality and did not look good on the preview site, I requested another image but this was poorly sized and pixelated.
I managed to get a much clearer image using image manipulation and AI software.

### Still to test upon deployment

- nav bar dropdown on screen sizes below 332px is a pain in the ass as it the dropdown does not ocnnedct to the nav bar making it look not great

- homepage styling on screens below 450px the buttons go out of the image this may be to do with my cody and home-content heigh calculations??
