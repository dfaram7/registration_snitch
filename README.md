# registration_snitch
A civic tech project to create a Twitter botnet To highlight unusual UK company registration activity

## Backstory
[@reg_snitch](https://twitter.com/reg_snitch) is a Twitter bot account that posts network charts like the one below to highlight unusual UK company registration activity. "Unusual" was initially a large number of companies being registered at one location in a short space of time (but not a registration agent or accountant) or a single company officer registering multiple companies in a short space of time to different addresses.

![network_chart](https://pbs.twimg.com/media/FRRukz5WQAEQ-rW?format=jpg&name=large)

The bot was only running for 48 hours before some [research](https://myfilipinoemployer.co.uk/directors-home-addresses) was published suggesting that known fraudulent actors were changing their tactics to evade being flagged by @reg_snitch! (The causation is unproven but I like to think I played a part!)

Amending one bot's detection logic to find fraudulent or unusual activity would likely turn into a whack-a-mole exercise and could be easily evaded. However, a whole community of people developing their own logic and coming together as a botnet on Twitter to share and amplify each others findings is much more difficult to evade. Hence this project!

Other goals for the project include;

- Raising awareness of how UK company registrations can be abused by criminals and fraudsters

- Show how often sub-networks of MUCs (Mini Umbrella Companies) crop up daily

- Provide the sub-networks to the community as a starting point for budding OSINT analysts to do further research

- Apply some pressure to the UK government to tighten up the registration process

#joinosintbotnetwithus!!! (Please don't abuse/pollute the hashtag, you'll be helping the baddies!)

## Tutorial
A tutorial for non-techy people brand new to APIs, Python and Github will be written in due course. In the meantime if you are a bit more tech savvy there is a jupyter notebook for experimentation and a script to run. Personally I run the script on a Digital Ocean droplet and schedule it to run using crontab.

## Prerequisites
- A Companies House API [key](https://developer.company-information.service.gov.uk/get-started)
- Elevated Twitter [Credentials](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api)
- A droplet/machine/local environment with python3, pip and git (+ anaconda/jupyter if you want to use the notebook)
- Read all about the types of activity we are trying to highlight [here](https://www.umbrellacompanies.org.uk/mini-umbrella-companies-muc/), [here](https://myfilipinoemployer.co.uk/) and [here](https://twitter.com/greybrow53)

## Installation
1. Clone the repository
```git clone https://github.com/dfaram7/registration_snitch```

2. Install requirements.txt
```pip install -r requirements.txt```

3. Enter your Companies House API credentials in registration_snitcher.py with your favourite text editor

4. Enter your Twitter credentials in registration_snitcher.py with your favourite text editor

5. Edit the parameters of registration_snitcher.py or write your own detection logic to share your custom charts

6. Run the program (hopefully with no errors!, please use the issues tab if you get stuck)
```python3 registration_snitcher.py```

7. Consider running it as a [scheduled job](https://fireship.io/snippets/crontab-crash-course/)

8. Become part of a civic tech project for the greater good! Your twitter account will tweet your charts with #joinosintbotnetwithus and retweet other accounts which are doing the same!


If you would like to host the project on a Digital Ocean droplet and you haven't used them before, get $100 free credit [here](https://m.do.co/c/cabe5b3802f3)

[![DigitalOcean Referral Badge](https://web-platforms.sfo2.cdn.digitaloceanspaces.com/WWW/Badge%201.svg)](https://www.digitalocean.com/?refcode=cabe5b3802f3&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge)
