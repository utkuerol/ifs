# Interactive Feedback System: In-or-Out


<p align="center">
<img width="578" alt="Screenshot 2019-03-11 at 14 59 56" src="https://user-images.githubusercontent.com/29407306/111138663-80e91880-8580-11eb-88c2-8b7d088a51b6.png"></p>


The software project Interactive Feedback System (IFS) is developed as part of the module "Praxis der Softwareentwicklung" (Software Development Practice) at the Karlsruhe Institute of Technology. The main objective of the project is to provide a Web platform to evaluate Active Learning in which the classification results of OcalAPI (https://github.com/englhardt/OcalAPI.jl) are reassessed by user feedbacks and the user behaviour during this process is recorded.

Note that this is an external git repository of the project, hiding commit history. 

Other contributors of the project: Alaa Mousa, Ari Nubar Boyacioglu, Mazen Ebada, Melis Lekesiz

## Project Overview 

![Screenshot 2021-03-15 at 11 25 49](https://user-images.githubusercontent.com/29407306/111139266-39af5780-8581-11eb-9717-fefe22de8e95.png)

### Use Case Diagram (German)

![Screenshot 2021-03-15 at 11 36 30](https://user-images.githubusercontent.com/29407306/111140532-b7279780-8582-11eb-8993-4e4e97236e3e.png)

# Build Instructions

```
$ cd ifs   (project path)
$ sudo apt-get install python3-pip
$ sudo pip3 install virtualenv 
$ virtualenv --python=/usr/bin/python3.7 venv
$ source venv/bin/activate    # activates the newly created virtualenv 'venv 
$ pip3 install -r requirements.txt    # installs project dependencies. sadly not all dependencies are succesfully installed with this command. you'll need to install some dependencies manually
$ pip3 install pillow
$ pip3 install sklearn
$ pip3 install requests
$ pip3 install pandas

-> replace the content of _display.py located in venv/lib/python3.7/site-packages/mpld3/   (this prevents a reported library bug and adds a new style to it)

$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py migrate --run-syncdb
$ python manage.py runserver
```

# Notes Regarding Testing Modules

## Test Data

In order to make our system tests more realistic we use real data. To succesfully run system tests you need to download files below from:

https://ilias.studium.kit.edu/ilias.php?ref_id=895161&cmd=view&cmdClass=ilrepositorygui&cmdNode=gu&baseClass=ilrepositorygui

 - FOR MNIST: mnist_raw.json      in      mnist_PSE.zip
 
 - FOR HIPE: WashingMachine_PhaseCount_3_geq_2017-10-23_lt_2017-10-30.json    in      hipe-raw/output/geq_2017-10-23_lt_2017-10-30_raw
 
Then move them into ifs/test_data.

## test-settings

Run tests using test-settings.py instead of the default setting.py.

To do that use the command: python manage.py  test adminapp/system_tests.py --settings=ifs.test-settings

## Selenium

For testing with Katalon (Selenium IDE):

- Install Katalon Chrome Plugin or

- Install Chrome Driver and use in your test class in setUp method:  "self.driver = webdriver.Chrome("path/to/chrome/driver")"

# Screenshots 

![experiments](https://user-images.githubusercontent.com/29407306/111139122-053b9b80-8581-11eb-9244-33c9788ae125.jpeg)

<img width="1062" alt="Screenshot 2019-03-11 at 16 42 23" src="https://user-images.githubusercontent.com/29407306/111139155-108ec700-8581-11eb-985d-e653c54d9b11.png">

<img width="632" alt="Screenshot 2019-03-11 at 16 43 38" src="https://user-images.githubusercontent.com/29407306/111139176-184e6b80-8581-11eb-80e8-785893afdcde.png">
