import db_scripts

db_scripts.create_tables()

db_scripts.open_db()
db_scripts.execute(
    """
    INSERT INTO users (name, image, login, password, desciption_short, description)
    VALUES (
        'Мохіто', 'mohito.png', 'mohito', '12345', 'Смачний коктейль з м ятою', 'Цей коктейль поєднує в собі свіжість м яти та солодкість лайму.'
    )
   """
)
db_scripts.close_db()
