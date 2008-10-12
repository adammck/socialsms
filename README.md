This is an SMS-based group messaging system. Callers can list, create, join
groups, and send messages to groups while remaining anonymous. Unitard is
built on the [SmsApplication](http://github.com/adammck/smsapp) library,
which sends and receives via [PyKannel](http://github.com/adammck/pykannel)
or [PyGnokii](http://github.com/adammck/pygnokii).


### A Fairly Typical Session

	<< help
	>> join <GROUP>
       leave <GROUP>
       identify <NAME>
       list [my] groups
       list members of <GROUP>
       <GROUP> <MESSAGE>
    
	<< list groups
	>> Groups: CHICKS, DUDES, ADULTS, DEVS
	
	<< join dudes
	>> You must identify yourself before joining groups
	
	<< identify mudkip
	>> Your name is now "MUDKIP"
	
	<< join dudes
	>> You have joined the DUDES group
	
	<< list members of dudes
	>> Members of DUDES: ADAM, MARK, EVAN, MERRICK, CHRIS, MUDKIP

    << dudes oh wow, all you dudes are receiving my messages
	>> Your message was sent to the DUDES group (5 people)

