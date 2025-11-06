<img src="readmeimages/BudgetBuddyLogo.png" alt="drawing" width="200"/>
# Budget Buddy!
*Your buddy for budgeting*

This is the Readme! There isn't much content here we **Budgeted** all of our time to make a good app

## Features
### Dashboard
*All you need at a glance*
<img src="readmeimages/budgetbuddy1.png" alt="drawing" width="400"/>

Tired of page after page to use the most basic features of a product? Our dashboard is compact and convenient, providing fast and easy insights, metrics and pretty visuals you want to see including unique, bite sized AI powered tips! 

### Expenses
<img src="readmeimages/budgetbuddy2.png" alt="drawing" width="400"/>

Whether you're feeling nostaligic for spreadheets of old, or you need some more controls (probably cause you punched in 4000 instead of 40.00, lets be real), the expenses tab has got you covered, giving you a nice, neat, no-nonsense of what you've spent your hard earned cash and what you want to add to make your insights more powerful

### Insights 
<img src="readmeimages/budgetbuddy3.png" alt="drawing" width="400"/>

If you like pretty graphs, youre gonna love the insights page! This page is dedicated to giving you the most comprehensive overview of your finances as well as how you spend your money as well as powerful tools to help you better spend your money

<img src="readmeimages/budgetbuddy5.png" alt="drawing" width="400"/>

When it comes to cruncing knowledge, there's nothing better than leverageng the best number-crunching research finding inventions there is out there. Powered by perplexity's sonar AI, this AI will answer your questions one by one while taking into account all the data that you've provided BudgetBuddy to crunch the number so you dont have to, giving you some of the most well reaserched insights possible.

### Categories
<img src="readmeimages/budgetbuddy4.png" alt="drawing" width="400"/>

If you want to fileter by category and see spending in a neat little category based graph, this is the page for you.

### Quality of life
<img src="readmeimages/budgetbuddy6.png" alt="drawing" width="400"/>

Light mode for If you like scorching your eyes

<img src="readmeimages/budgetbuddy7.png" alt="drawing" width="400"/>

we also optimized for mobile 

<img src="readmeimages/budgetbuddy8.png" alt="drawing" width="400"/>

and the navbar is here too, it took a lot of code, please appreciate this

## Installation
this is gonna be step by step build instructons, if you have any technical knowlage, everything SHOULD be understanadble cause of the requirements, you also need a .env with a perplexity API key and secretkey (PERPLEXITY_API_KEY and ServerSecret)
### Requirements

**A couple of these are from testing, so arent used but are still on the install list because I dont care**

literally just run these terminal commands and you're set (these are on a unix based system, if you run windows sorry, just use linux bro, its so worth it)
```
git clone https://github.com/Arsenaet/BudgetBuddy
cd BudgetBuddy
pip install -r requirements.txt
pip install sqlalchemy flask_sqlalchemy (was messed up in build requirements lol)
make your .env file with your secrets and API keys as outlined above using your text editor of choice (hopefully neovim)
flask run -h app.py
```
Easy as that, your server is deplopyed, all you gotta do now is go to your web browser of choice and open localhost to port 8000 
