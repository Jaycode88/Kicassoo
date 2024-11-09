
## unsolved bugs

- nav bar dropdown on screen sizes below 332px is a pain in the ass as it the dropdown does not ocnnedct to the nav bar making it look not great

- homepage styling on screens below 450px the buttons go out of the image this may be to do with my cody and home-content heigh calculations??


## Notes

- to import products from store use terminal command "python manage.py import_products"

- in checkout to create Draft/test order set "confirm" to false in services.py line 48 and views.py line 30

- Details and category need to be added manually to the imported products


- checkout is very robust it stores the order as soon as a person enters their card details with a status of payment pending then the webhook carries the order number on receipt of a succesful payment webhook the order payment status is updated to completed and the order is sent to printful via the API.. I did originally put all of the order info onto the webhook but this caused problems due to the 500 characther limit the stripe webhook is restricted to. Another great benefit of the way that checkout is setup is that If a user's payment fails and they do not choose to use another card and complete the order, You will have the order stored with a payment failed staus from here you can aquire the user's information  such as email address and send them reminders or discount  to encourage completion of order.

- mention the webhook error in solved bugs, I had a problem when there were many items(over 4 or 5) on an order i got an error due to the stripe webhook having a character limit of 500, I had set the webhook up to contain all of the order data including the items but this is what was causing the error. To solve the issue I implemented that as soon as the user submits their card details the order is created with a payment pending status, then that allowed for the webhook to only need to hold the order number. When the webook returns a payment intent succeeded with the order number only then is the order payment status updated to completed and the order is sent to printful for fulfillment.





# Testing
Return back to the [README.md](README.md) file.

I have used various tools to Test Funcionality, Validity and responsiveness. I have been sure to check all layouts, colours, text, forms, links, buttons are functioning on all devices and screen sizes that I have tested.

## Code Validation

### HTML
All pages files have been tested with [W3C Markup Validation Service](https://validator.w3.org/).







## Bugs
### Open Issues


### Solved bugs
#### Font package
I had an issue When the user hovered over a button, all the text changed to black except for the letter "N". I diagnosed this to be a font package issue as when I load the buttons with a different font the problem did not exist. The other option I found was to remove the text transform to uppercase class. 
I discussed with client which resolution they preffered and it was chosen to remove the uppercase transform.

#### Logo
I recieved an image to use as a logo but this was not of sufficient quality and did not look good on the preview site, I requested another image but this was poorly sized and pixelated.
I managed to get a much clearer image using image manipulation and AI software.
