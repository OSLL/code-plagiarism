import threading
import datetime
from _thread import start_new_thread

class myThread (threading.Thread):
   def __init__(self, name, counter):
       threading.Thread.__init__(self)
       self.threadID = counter
       self.name = name
       self.counter = counter

   def run(self):
       print("Starting " + self.name)
       print_date(self.name, self.counter)
       print("Exiting " + self.name)

def factorial(n, threadId):
    if n < 1:
        print('Thread', threadId)
        return 1
    else:
        returnNumber = n * factorial(n - 1, threadId)
        print(str(n) + '! = ' + str(returnNumber))
        return returnNumber

#start_new_thread(factorial, (5, 1))
#start_new_thread(factorial, (4,2))

def print_date(threadName, counter):
    datefields = []
    today = datetime.date.today()
    datefields.append(today)
    print(threadName, counter, datefields[0])

thread1 = myThread("Thread", 1)
thread2 = myThread("Thread", 2)

thread1.start()
thread2.start()

thread1.join()
thread2.join()
print("Exiting the Program!!!")
