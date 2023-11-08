## Digital diary

### Users table:
* UserID (primary key)
* Name : _str_
* Email : _str_
* Age : _int_

### Diary entries table:
* EntryID (primary key)
* TextContent : _str_
* MoodRating : _float_ (0.0-10.0) # Rate your mood today from 0 to 10
* BodyTemperature : _float_ # I don't know
* Date : _datetime_
* UserID (foreign key referencing the UserID in the Users table)
