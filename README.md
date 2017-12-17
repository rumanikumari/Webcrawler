Database used: MongoDB
running on port 27017
Collections required: "CompanyDetails"

Rest Enpoints:
1) To gather startup names and few details from the website
route: /company
params: filter_data[featured]=Featured
filter_data[company_types][]=Startup
filter_data[locations][]=1904-Bengaluru
filter_data[markets][]=E-Commerce
filter_data[teches][]=Javascript
filter_data[stage]=Acquired
filter_data[raised][min]=10000
filter_data[raised][max]=100000000
filter_data[signal][min]=0
filter_data[signal][max]=10

2)To populate the domain names for the company from database whose domain was not found while gathering the company details in the previous end point
route: /populateDomain
