import time
from enum import Enum

from eaxtension import LogE

class TimeCheckerState(Enum):
    clear = 0
    running = 1
    pause = 2
    end = 3

class TimeChecker:
    time_log = []                   # Logging checker actions
    running_stamp = 0               # Time stamp for measuring progress of running time
    running_acc = 0
    pause_stamp = 0                 # Time stamp for measuring progress of pausing time
    pause_acc = 0
    limit = 0                       # Time limitation
    __state = TimeCheckerState(0)   # Internal state of time checker
    
    def __init__(self, limit: int, print_log=False):
        self.limit = limit
        self.print_log = print_log
    
    # Record checker action with time stamp.
    def record_time_log(self, current_time):
        self.time_log.append({self.__state, current_time})
        if self.print_log:
            LogE.d(self.__state, self.get_time())
        return current_time
    
    # Description: Start the tImer. It works when the checker has been cleared.
    def start(self):
        current_time = time.time()
        if self.__state.name == "clear":
            self.running_stamp = current_time            # Record current time.
            self.__state = TimeCheckerState.running     # Change the internal state to 'running'.
            self.record_time_log(current_time)          # Record the action.
            
        else:
            raise AssertionError("초기화 하고 쓰세요 ^^")

    # Description: Pause the timer. It works when the checker is running.
    def pause(self):
        current_time = time.time()
        if self.__state.name == "running":
            self.running_acc += current_time - self.running_stamp       # Suspend mesurement of running timer.
            self.pause_stamp = current_time                         # Start mesuring of pause timer.
            self.__state = TimeCheckerState.pause                    # Change the internal state to 'pause'.
            self.record_time_log(current_time)                       # Record the action.
        else:
            raise AssertionError("실행중이 아니면 멈출 수 없음")
      
    # Description: Resume the mesurement of running timer. It works when the checker had been paused.
    def resume(self):
        current_time = time.time()
        if self.__state.name == "pause":
            self.pause_acc += current_time - self.pause_stamp      # Suspend mesurement of pause timer.
            self.running_stamp = current_time                         # Start mesuring of running timer.
            self.__state = TimeCheckerState.running                 # Change the internal state to 'running'.
            self.record_time_log(current_time)                      # Record the action.
        else:
            raise AssertionError("멈춘게 아니면 재개할 수 없음")

    # def end(self):
    #     current_time = time.time()
    #     if self.__state.name == "running":
    #         self.running_stamp = current_time - self.running_stamp
    #         self.__state = TimeCheckerState.end
    #         self.record_time_log(current_time)
    #     elif self.__state.name == "pause":
    #         self.running_stamp = current_time - self.running_stamp
    #         self.pause_stamp = current_time - self.pause_stamp
    #         self.__state = TimeCheckerState.end
    #     else:
    #         raise AssertionError("도는 중이어야 멈추지")

    def clear(self):
        self.running_stamp = 0
        self.pause_stamp = 0
        self.running_acc = 0
        self.pause_acc = 0
        self.__state = TimeCheckerState.clear

    def restart(self):
        if self.print_log:
            LogE.g("restarted", "")
        self.clear()
        self.start()

    def is_over(self) -> bool:
        current_time = time.time()
        
        if self.__state.name == "running":
            time_progress = (current_time - self.running_stamp + self.running_acc) #- (self.pause_acc)
        elif self.__state.name == "pause":
            time_progress = (self.running_acc) - (current_time - self.pause_stamp )#+ self.pause_acc)
        else:
            return False
        
        time_progress = time_progress if time_progress > 0 else 0
        
        if (time_progress >= self.limit):
            return True
        else:
            return False
        
    def get_time(self) -> int:
        current_time = time.time()
        if self.__state.name == "running":
            time_progress = (current_time - self.running_stamp + self.running_acc) #- (self.pause_acc)
        elif self.__state.name == "pause":
            time_progress = (self.running_acc) - (current_time - self.pause_stamp )#+ self.pause_acc)
        else:
            return 0
        
        time_progress = time_progress if time_progress > 0 else 0
        # print("gettime", time_progress, current_time, self.running_stamp, self.running_acc, self.pause_acc, self.pause_stamp)
        
        return time_progress
    
    
def clear_timers(timer_list):
    for timer in timer_list:
        timer.clear()

def start_timers(timer_list):
    for timer in timer_list:
        timer.start()

if __name__ == "__main__":
    tc = TimeChecker(3)
    tc.start()
    time.sleep(1)
    print(tc.is_over())
    print(time.time() - tc.running_stamp, tc.pause_stamp)
    tc.clear()
    tc.start()
    tc.pause()
    time.sleep(1)
    tc.resume()
    time.sleep(4)
    print(tc.is_over())
    print(time.time() - tc.running_stamp, tc.pause_stamp)
    tc.clear()