--
-- PostgreSQL database dump
--

-- Dumped from database version 15.1
-- Dumped by pg_dump version 15.1

-- Started on 2022-12-11 02:42:29

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 5 (class 2615 OID 24769)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

--
-- TOC entry 3354 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 214 (class 1259 OID 24774)
-- Name: allergen; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.allergen (
    allergenid integer NOT NULL,
    allergenname character varying(20)
);


ALTER TABLE public.allergen OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 24778)
-- Name: food; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.food (
    barcodeno integer NOT NULL,
    foodname character varying(20),
    brand character varying(20),
    weightvolume integer,
    ingredients character varying(500)
);


ALTER TABLE public.food OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 24782)
-- Name: food_contains; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.food_contains (
    barcodeno integer,
    allergenid integer
);


ALTER TABLE public.food_contains OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 24785)
-- Name: nutrition; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nutrition (
    fat integer,
    protein integer,
    carbs integer,
    calorie integer,
    barcodeno integer NOT NULL
);


ALTER TABLE public.nutrition OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 24789)
-- Name: person; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.person (
    userid integer NOT NULL,
    e_mail character varying(20),
    personname character varying(20),
    personsurname character varying(20),
    telephoneno character varying(20),
    saltedpassword character varying(20),
    height integer,
    weight integer
);


ALTER TABLE public.person OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 24793)
-- Name: personhasallergen; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.personhasallergen (
    allergenid integer,
    userid integer
);


ALTER TABLE public.personhasallergen OWNER TO postgres;

--
-- TOC entry 3343 (class 0 OID 24774)
-- Dependencies: 214
-- Data for Name: allergen; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.allergen (allergenid, allergenname) FROM stdin;
1	gluten
2	findik
\.


--
-- TOC entry 3344 (class 0 OID 24778)
-- Dependencies: 215
-- Data for Name: food; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.food (barcodeno, foodname, brand, weightvolume, ingredients) FROM stdin;
1	ekmek	firinci	200	un
\.


--
-- TOC entry 3345 (class 0 OID 24782)
-- Dependencies: 216
-- Data for Name: food_contains; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.food_contains (barcodeno, allergenid) FROM stdin;
1	1
1	2
\.


--
-- TOC entry 3346 (class 0 OID 24785)
-- Dependencies: 217
-- Data for Name: nutrition; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.nutrition (fat, protein, carbs, calorie, barcodeno) FROM stdin;
20	10	75	300	1
\.


--
-- TOC entry 3347 (class 0 OID 24789)
-- Dependencies: 218
-- Data for Name: person; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.person (userid, e_mail, personname, personsurname, telephoneno, saltedpassword, height, weight) FROM stdin;
31	\N	İsmail	Öz	\N	313131	\N	\N
\.


--
-- TOC entry 3348 (class 0 OID 24793)
-- Dependencies: 219
-- Data for Name: personhasallergen; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.personhasallergen (allergenid, userid) FROM stdin;
1	31
\.


--
-- TOC entry 3192 (class 1259 OID 24777)
-- Name: xpkallergen; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX xpkallergen ON public.allergen USING btree (allergenid);


--
-- TOC entry 3193 (class 1259 OID 24781)
-- Name: xpkfood; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX xpkfood ON public.food USING btree (barcodeno);


--
-- TOC entry 3194 (class 1259 OID 24788)
-- Name: xpknutrition; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX xpknutrition ON public.nutrition USING btree (barcodeno);


--
-- TOC entry 3195 (class 1259 OID 24792)
-- Name: xpkperson; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX xpkperson ON public.person USING btree (userid);


--
-- TOC entry 3196 (class 2606 OID 24796)
-- Name: food_contains r_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.food_contains
    ADD CONSTRAINT r_1 FOREIGN KEY (barcodeno) REFERENCES public.food(barcodeno) ON DELETE SET NULL;


--
-- TOC entry 3197 (class 2606 OID 24801)
-- Name: food_contains r_2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.food_contains
    ADD CONSTRAINT r_2 FOREIGN KEY (allergenid) REFERENCES public.allergen(allergenid) ON DELETE SET NULL;


--
-- TOC entry 3199 (class 2606 OID 24811)
-- Name: personhasallergen r_3; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personhasallergen
    ADD CONSTRAINT r_3 FOREIGN KEY (allergenid) REFERENCES public.allergen(allergenid) ON DELETE SET NULL;


--
-- TOC entry 3200 (class 2606 OID 24816)
-- Name: personhasallergen r_4; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personhasallergen
    ADD CONSTRAINT r_4 FOREIGN KEY (userid) REFERENCES public.person(userid) ON DELETE SET NULL;


--
-- TOC entry 3198 (class 2606 OID 24806)
-- Name: nutrition r_5; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrition
    ADD CONSTRAINT r_5 FOREIGN KEY (barcodeno) REFERENCES public.food(barcodeno);


--
-- TOC entry 3355 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


-- Completed on 2022-12-11 02:42:29

--
-- PostgreSQL database dump complete
--

