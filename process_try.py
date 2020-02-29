import random

num_lanes = 3
num_booths = 4
total_time = 10000

def random_choose(distribution, ban_list):
    # Function for ramdom selection from a listed distribution
    # ban_list is forbidden choices, e.g. crowed booths
    dice = random.random()
    base = 0
    for i in range(len(distribution)):
        if (base + distribution[i] >= dice and i not in ban_list):
            return i
        else:
            base += distribution[i]
            continue
    else:
        return -1



class booth(object):
    max_queue = 10 # maximum number of cars waiting to pay
    pay_time = 1 # average time for one car to pass the booth
    
    def __init__(self):
        self.num_queue = 0 # no car is waiting at first
        self.process_timer = 0 # used in process method
        self.average_len = 0 # average queueing length
        self.total_passage = 0 # total amount of cars passed
    
    def is_full(self):
        if (self.num_queue < self.max_queue):
            return 0 # can add more cars
        else:
            return 1 # can't hold more cars
    
    def add_car(self):
        self.num_queue += 1
    
    def process(self): # that is, to take money
        # Mind the sequence here.
        if (self.num_queue == 0):
            self.process_timer = 0
        elif (self.process_timer == self.pay_time):
            self.num_queue -= 1
            self.process_timer = 0
            self.total_passage += 1
        else:
            self.process_timer += 1
    
    def update_average_len(self):
        self.average_len += self.num_queue / total_time



class lane(object):
    alpha = 0.5 # from discrete Poisson distribution, alpha is the expected amount of cars per timestep

    def __init__(self, choice_distribution):
        self.choice_distribution = choice_distribution 
        # a list of probability distribution for booth selection
        self.crowded = False
        # if a car has nowhere to go, it stucks in the lane and thus making the lane crowded
        self.num_stuck = 0
        # number of cars stuck in the lane

    def spawn_car(self):
        if (not self.crowded):
            # each lane has the probability alpha to spawn a car per timestep
            if (random.random() > self.alpha):
                return 1
            else: return 0
        else: # crowded
            if (random.random() > self.alpha):
                self.num_stuck += 1 # another car comes and gets stuck too
            return 1 # when crowded, a lane always has a car to send to booths

    def choose_booth(self, ban_list):
        choice = random_choose(self.choice_distribution, ban_list)
        if (choice != -1): # there are booths to go to
            if (self.num_stuck > 0):
                self.num_stuck -= 1 # car waiting in the lane decreases
            return choice
        else: # some cars have no place to go
            if(self.num_stuck == 0):
                self.num_stuck = 1
                # this situation tells that at least one car is stuck, but can't tell the exact number
            self.crowded = True
            return -1 # -1 means stuck

    def check_crowded(self):
        if(self.num_stuck == 0 and self.crowded == True):
            self.crowded = False
        elif(self.num_stuck > 0 and self.crowded == False):
            self.crowded = True


''' 正片开始 '''
# First create lane and booths
booths = []
for i in range(num_booths):
    booths.append(booth())

lanes = []
distributions = [[0.75, 0.25, 0, 0], [0.25, 0.5, 0.25, 0], [0, 0.25, 0.5, 0.25]]
# very naive assignment
for i in range(num_lanes):
    lanes.append(lane(distributions[i])) # create a lane with given distribution

# Second, some static variables for performance analysis
crowed_time = 0 # total crowded time of all lanes
car_passed = 0 # total number of car passage
overall_average_queue = 0

# Third, begin the main loop
for timestep in range(total_time):
    # Update states and statistics
    ban_list = [] # list of booth index that are full
    for i in range(len(booths)):
        booths[i].process() # pocess at the beginning of a time step
        if (booths[i].is_full()):
            ban_list.append(i) # notice that ban_list will not shrink within a timestep
        booths[i].update_average_len()
    for l in lanes:
        l.check_crowded() # check if the lane is (still) crowded
        if (l.crowded):
            crowed_time += 1
    # Spawn cars in a random sequence
    sequence = list(range(num_lanes))
    random.shuffle(sequence)
    for id in sequence:
        if (lanes[id].spawn_car() == 1): # a car comes
            choice = lanes[id].choose_booth(ban_list) # the car choose a booth, or get stuck
            if (choice != -1): # not stuck
                booths[choice].add_car() # the car goes to the booth and wait
                if booths[choice].is_full():
                    ban_list.append(choice)
                    # when the booth is chosen, it may become full
            # else the car gets stuck, already handled
        # else no car comes
# Update total car passage
for b in booths:
    car_passed += b.total_passage
    overall_average_queue += b.average_len
average_queue = overall_average_queue / num_booths
# Display statistics
print('Total thoughput: {}'.format(car_passed))
print('Total crowded time: {}'.format(crowed_time))
print('Average queue length at all booths: {}'.format(average_queue))
