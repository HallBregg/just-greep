create table if not exists offer
(
	id bigserial not null
		constraint offer_pk
			primary key,
	title text not null,
	skills json not null,
	remote boolean,
	salary_from integer,
	salary_to integer,
	salary_currency text,
	experience text,
	body text
);

alter table offer owner to postgres;

create unique index if not exists offer_id_uindex
	on offer (id);

create table if not exists company
(
	id bigserial not null
		constraint company_pk
			primary key,
	name text not null,
	size integer,
	country text,
	city text not null,
	street text,
	url text,
	longitude text,
	latitude text
);

alter table company owner to postgres;

create unique index if not exists company_id_uindex
	on company (id);

create table if not exists general
(
	id serial not null
		constraint general_pk
			primary key,
	offer_id bigint
		constraint offer_id
			references offer
				on update cascade on delete set null,
	company_id bigint
		constraint company_id
			references company
				on update cascade on delete set null,
	url_id text,
	download_number bigint not null,
	published text,
	download_date text
);

alter table general owner to postgres;

create unique index if not exists general_id_uindex
	on general (id);
