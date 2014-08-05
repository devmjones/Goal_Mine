Goal_Mine
=========

### Why Goal Mine?

Before Hackbright I taught Special Education for 7 years, and I would have to take data on each of my students federally mandated individualized education plan goals. I would make my own data sheets for each goal, put them in a binder, carry it around, pencil in data throughout the day and then transfer it all into an excel spreadsheet when it came time for progress reports. I had looked for an online tool for data collection, but all I could find was pre-made spreadsheets. When it came time to pick a project I knew I wanted to make a tool to simplify and streamline some kind of process, so I made Goal Mine. 

### What is Goal Mine?

Goal Mine is a data collection and report generating web app. The back end is Python with Flask as it’s framework, and all data is stored in a SQLite database. The user interface is HTML and CSS supported by Bootstrap for responsiveness, and the forms are made in Jinja, Flask’s templating language. JavaScript and jQuery were used for many of the data collection tools. 

###How is it used?

A teacher can add students to their class and upon visiting the student page they can view that student’s existing goals, take data, edit, delete, generate a report, or make a new goal. They can also add “markers”, which record any life events that may affect a student’s progress. 

When a new goal is created, additional fields can be added with a jQuery backed field incrementer. The teacher then selects which type of data collection tool is needed for each item, and when they hit submit it generates a custom data sheet by triggering macro functions in Jinja. 

The data collection page can have multiple tools based on what the teacher selected. I used jQuery to make increment buttons for the tally, true/false, and stopwatch tools, the range tool is a radio button likert scale, and the narrative is a time stamped journal. 

To generate a report a data range is selected and a variety of class, instance, and static methods break down and process the raw data for that goal. Additional Jinja macros display the total instances of data collection, the average result, a breakdown of percentages for each result, and the total record for that goal. Any markers that occurred during that date range are displayed so the teacher can decide what if any effect they may have had on a students progress.  

###What's next for Goal Mine?

Integrating D3 or Google Visualization API to visually represent data, increase security with Flask Security, add additional permissions for multiple users, incorporate WTForms for more thorough validation, and make Goal Mine available for open source usage. 


Screenshots:

Homepage
<a href="http://imgur.com/kNocVkW"><img src="http://i.imgur.com/kNocVkW.jpg" title="Hosted by imgur.com"/></a>

Classroom
<a href="http://imgur.com/RTcZjRc"><img src="http://i.imgur.com/RTcZjRc.jpg" title="Hosted by imgur.com"/></a>

Student Page
<a href="http://imgur.com/0BmXHHS"><img src="http://i.imgur.com/0BmXHHS.jpg" title="Hosted by imgur.com"/></a>

Markers
<a href="http://imgur.com/uTnV1al"><img src="http://i.imgur.com/uTnV1al.jpg" title="Hosted by imgur.com"/></a>

Goal Creation
<a href="http://imgur.com/8xHTfDO"><img src="http://i.imgur.com/8xHTfDO.jpg" title="Hosted by imgur.com"/></a>

Data Collection
<a href="http://imgur.com/evjgGuW"><img src="http://i.imgur.com/evjgGuW.jpg" title="Hosted by imgur.com"/></a>

Report Generation with Markers
<a href="http://imgur.com/a1s595r"><img src="http://i.imgur.com/a1s595r.jpg" title="Hosted by imgur.com"/></a>

Report Summary 1
<a href="http://imgur.com/qJneAlZ"><img src="http://i.imgur.com/qJneAlZ.jpg" title="Hosted by imgur.com"/></a>

Report Summary 2
<a href="http://imgur.com/TBmm7gl"><img src="http://i.imgur.com/TBmm7gl.jpg" title="Hosted by imgur.com"/></a>
