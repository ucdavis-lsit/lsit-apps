CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id uuid DEFAULT uuid_generate_v4 (),
    email character varying(255) NULL,
    domain uuid NOT NULL,
    created timestamp without time zone NOT NULL DEFAULT current_timestamp,
    last_modified timestamp without time zone NOT NULL DEFAULT current_timestamp,
    last_sign_in timestamp without time zone,
    PRIMARY KEY (id),
    FOREIGN KEY (domain) REFERENCES domains(id)
);

CREATE TABLE domains (
    id uuid DEFAULT uuid_generate_v4 (),
    name character varying(255) NULL,
    PRIMARY KEY (id)
);

CREATE TABLE subdomains (
    id uuid DEFAULT uuid_generate_v4 (),
    name character varying(255) NULL,
    domain uuid NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (domain) REFERENCES domains(id)
);

--create function trigger to change a timestamp value upon an update
CREATE OR REPLACE FUNCTION set_last_modified()
RETURNS TRIGGER AS $$
BEGIN
  NEW.last_modified = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--create a trigger to execute the function
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON public.Users
FOR EACH ROW
EXECUTE PROCEDURE set_last_modified();