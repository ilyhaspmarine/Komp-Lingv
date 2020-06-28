#encoding "utf8"

Person -> Word<kwtype=person> interp (Person.Person);

Position -> 'заместитель'|'зам'|'зампредседатель'|'председатель'|'зампред'|'депутат'|'директор'|'губернатор'|'мэр';

PersonPos -> Position<c-agr[1]> AnyWord* Person<c-agr[1]>|Person<c-agr[1]> AnyWord* Position<c-agr[1]>;
PersonPosPlus -> AnyWord* PersonPos;
PersonPoses -> PersonPos PersonPosPlus*;

TopicText -> AnyWord* PersonPoses AnyWord*;

PersonTopic -> TopicText interp (Person.Text::not_norm);