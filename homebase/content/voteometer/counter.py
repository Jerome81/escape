class Counter:

    total = 0
    total_votes = 0
    last_vote = 0
    is_button_light_on = False

    def vote(self, number):
        self.turn_button_light_off()
        self.last_vote = number * 33
        self.display_last_vote()
        self.total = self.total + self.last_vote
        self.total_votes = self.total_votes + 1
    
    def average(self):
        if self.total_votes == 0:
            return 0
        else:
            return round(self.total / self.total_votes)
    
    def display_last_vote(self):
        print("Last vote: %s" % self.last_vote)
        #TODO play LED animation
    
    def play_loaded_animation(self):
        print("loaded")
        #TODO play LED animation

    def show_average(self):
        average = self.average()
        print("Average is: %s" % average)
        #TODO Display on LED
    
    def turn_button_light_on(self):
        #TODO turn button lights on
        print("Turning button lights on")
        
    def turn_button_light_off(self):
        #TODO turn button lights off
        print("Turning button lights off")
        