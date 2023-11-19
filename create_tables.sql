CREATE TABLE Users (
    UserID SERIAL PRIMARY KEY,
    Name VARCHAR(255),
    Email VARCHAR(255),
    Age INT
);

CREATE TABLE DiaryEntries (
    EntryID SERIAL PRIMARY KEY,
    TextContent TEXT,
    MoodRating FLOAT CHECK (MoodRating >= 0.0 AND MoodRating <= 10.0),
    BodyTemperature FLOAT,
    Date TIMESTAMPTZ,
    UserID INT,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);