from selenium import webdriver
import unittest

class NewVisitortest(unittest.TestCase):

	#Special method that runs before our test starts
	def setUp(self):
		self.browser = webdriver.Firefox()
		#Wait for three seconds before testing
		#provides time for content to appear on the browser
		self.browser.implicitly_wait(3)	

	#Special method that runs after the test finishes
	def tearDown(self):
		self.browser.quit()

	#All the methods to be tested start with test_
	def test_can_start_a_list_and_retrieve_it_later(self):
		self.browser.get('http://localhost:8000')

		self.assertIn("To-Do",self.browser.title)
		self.fail("Finish the test!")
if __name__=='__main__':
	unittest.main()

