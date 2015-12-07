#!/usr/bin/python
#coding:utf-8

#author:	gavingeng
#date:		2011-12-03 10:50:01 

class Person:

	def __init__(self):
		print("init")
		self.hehe="aa"

	@staticmethod
	def sayHello(hello):
		if not hello:
			hello='hello'
		print("i will sya "+hello)


	@classmethod
	def introduce(clazz,self):
		clazz.sayHello(self.hehe)
		print("from introduce method")




def main():
	person=Person()
	person.introduce()
	#Person.hello("self.hello")	#TypeError: unbound method hello() must be called with Person instance as first argument (got str instance instead)
	
	

if __name__=='__main__':
	main()
