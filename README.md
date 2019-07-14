# Start Instructions

Django, DB and OcalAPI are already running on the server. Only an ssh-tunneling is required to access the website. 

Superuser is "ifs", password to ifs is "ifsifsifs"

A normal test user is "user", password to user is "useruser"

 # forward ssh remote:8000 to localhost:8000


*  ssh -N -L 8000:127.0.0.1:8000 erol@ravenclaw.ipd.kit.edu     #password= erol01ab

---

 # start ocalapi docker


*  ssh erol@ravenclaw.ipd.kit.edu -p22    #password= erol01ab

*  .. (start docker as explained in api documentation)

---

# Build Instructions From Scratch


*  cd ifs   (project path)
 
*  sudo apt-get install python3-pip

*  sudo pip3 install virtualenv 

*  virtualenv --python=/usr/bin/python3.7 venv

*  source venv/bin/activate    (activates the newly created virtualenv 'venv')

*  pip3 install -r requirements.txt (installs project dependencies. sadly not all dependencies are succesfully installed with this command. you'll need to install some
  dependencies manually)

* pip3 install pillow
* pip3 install sklearn
* pip3 install requests
* pip3 install pandas

*  replace the content of _display.py located in venv/lib/python3.7/site-packages/mpld3/   (this prevents a reported library bug and adds a new style to it)

*  python manage.py makemigrations
*  python manage.py migrate
*  python manage.py migrate --run-syncdb
*  python manage.py runserver


# Notes Regarding Testing Modules

* Test Data

In order to make our system tests more realistic we use real data. To succesfully run system tests you need to download files below from:

https://ilias.studium.kit.edu/ilias.php?ref_id=895161&cmd=view&cmdClass=ilrepositorygui&cmdNode=gu&baseClass=ilrepositorygui

 FOR MNIST: mnist_raw.json      in      mnist_PSE.zip
 
 FOR HIPE: WashingMachine_PhaseCount_3_geq_2017-10-23_lt_2017-10-30.json    in      hipe-raw/output/geq_2017-10-23_lt_2017-10-30_raw
 
Then move them into ifs/test_data.

* test-settings

Run tests using test-settings.py instead of the default setting.py.

To do that use the command: python manage.py  test adminapp/system_tests.py --settings=ifs.test-settings

* Selenium

For testing with Katalon (Selenium IDE):

Install Katalon Chrome Plugin or

Install Chrome Driver and use in your test class in setUp method:  "self.driver = webdriver.Chrome("path/to/chrome/driver")"

