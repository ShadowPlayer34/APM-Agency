import sqlite3

# Function to create tables in the database
def create_tables():
    connection_params = {"database": "mydb.sqlite3"}

    # Connect to the database
    connect = sqlite3.connect(connection_params["database"])
    cursor = connect.cursor()
    cursor.execute('''
        CREATE TABLE Клиент (
    ClientID INT PRIMARY KEY,
    FullName VARCHAR(255) NOT NULL,
    PhoneNumber VARCHAR(20),
    Address VARCHAR(255)
);
    ''')

    cursor.execute('''
        CREATE TABLE Риэлтор (
    RealtorID INT PRIMARY KEY,
    FullName VARCHAR(255) NOT NULL
);
    ''')

    cursor.execute('''
       CREATE TABLE Контракт (
    ContractID INT PRIMARY KEY,
    ClientID INT REFERENCES Client(ClientID),
    StartDate DATE,
    EndDate DATE
);
    ''')

    cursor.execute('''
        CREATE TABLE Объект (
    PropertyID INT PRIMARY KEY,
    Description TEXT,
    ConstructionDate DATE
);
    ''')

    cursor.execute('''
        CREATE TABLE Просмотр (
    ViewingID INT PRIMARY KEY,
    ClientID INT REFERENCES Client(ClientID),
    RealtorID INT REFERENCES Realtor(RealtorID),
    ViewingDate DATE
);
    ''')

    cursor.execute('''
        INSERT INTO Клиент (ClientID, FullName, PhoneNumber, Address) VALUES
(1, 'Иван Иванов', '1234567890', 'ул. Главная, д. 1'),
(2, 'Мария Петрова', '9876543210', 'пр. Центральный, д. 5');
    ''')

    cursor.execute('''
        INSERT INTO Риэлтор (RealtorID, FullName) VALUES
(1, 'Анна Смирнова'),
(2, 'Дмитрий Козлов');
    ''')

    cursor.execute('''
        INSERT INTO Объект (PropertyID, Description, ConstructionDate) VALUES
(1, 'Красивый дом', '2020-01-01'),
(2, 'Просторная квартира', '2018-05-15');
    ''')

    cursor.execute('''
        INSERT INTO Контракт (ContractID, ClientID, StartDate, EndDate) VALUES
(1, 1, '2022-01-01', '2022-12-31'),
(2, 2, '2022-02-01', '2022-11-30');
    ''')

    cursor.execute('''
        INSERT INTO Просмотр (ViewingID, ClientID, RealtorID, ViewingDate) VALUES
(1, 1, 1, '2022-03-15'),
(2, 2, 2, '2022-04-20');
    ''')

    # Commit changes and close connection
    connect.commit()
    cursor.close()
    connect.close()

if __name__ == "__main__":
    # Call the function to create tables
    create_tables()

    print("Tables created and data inserted successfully.")