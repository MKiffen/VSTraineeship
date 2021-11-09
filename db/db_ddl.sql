CREATE DATABASE booking;
USE booking;
CREATE TABLE HOTEL
(
  hotel_id       INT          NOT NULL AUTO_INCREMENT,
  hotel_naam     VARCHAR(100) NULL    ,
  hotel_adres    VARCHAR(250) NULL    ,
  hotel_incheck  TIME         NULL    ,
  hotel_uitcheck TIME         NULL    ,
  hotel_externid TEXT         NULL    ,
  reis_id        INT          NOT NULL,
  PRIMARY KEY (hotel_id)
);

CREATE TABLE NS
(
  ns_id           INT     NOT NULL AUTO_INCREMENT,
  ns_vertrekijd   TIME    NULL    ,
  ns_aankomsttijd TIME    NULL    ,
  ns_duur         INT     NULL    ,
  ns_overstappen  TINYINT NULL    ,
  ns_prijs        INT     NULL    ,
  reis_id         INT     NOT NULL,
  PRIMARY KEY (ns_id)
);

CREATE TABLE REIS
(
  reis_id               INT         NOT NULL AUTO_INCREMENT,
  reis_vertrekstation   VARCHAR(50) NULL    ,
  reis_bestemming       VARCHAR(50) NULL    ,
  reis_vertrekvliegveld VARCHAR(50) NULL    ,
  reis_datumheen        DATE        NULL    ,
  reis_datumterug       DATE        NULL    ,
  reis_personen         TINYINT     NULL    ,
  reis_querytimestamp   TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (reis_id)
);

CREATE TABLE VLUCHT
(
  vlucht_id                INT         NOT NULL AUTO_INCREMENT,
  vlucht_vertrektijd       DATETIME    NULL    ,
  vlucht_aankomsttijd      DATETIME    NULL    ,
  vlucht_duur              INT         NULL    ,
  vlucht_prijs             FLOAT       NULL    ,
  vlucht_maatschappij      VARCHAR(50) NULL    ,
  vlucht_aankomstvliegveld VARCHAR(50) NULL    ,
  reis_id                  INT         NOT NULL,
  PRIMARY KEY (vlucht_id)
);

ALTER TABLE HOTEL
  ADD CONSTRAINT FK_REIS_TO_HOTEL
    FOREIGN KEY (reis_id)
    REFERENCES REIS (reis_id);

ALTER TABLE VLUCHT
  ADD CONSTRAINT FK_REIS_TO_VLUCHT
    FOREIGN KEY (reis_id)
    REFERENCES REIS (reis_id);

ALTER TABLE NS
  ADD CONSTRAINT FK_REIS_TO_NS
    FOREIGN KEY (reis_id)
    REFERENCES REIS (reis_id);