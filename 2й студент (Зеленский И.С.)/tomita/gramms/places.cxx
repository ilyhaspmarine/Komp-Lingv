#encoding "utf8"

Place -> Word<kwtype=place> interp (Place.Place); 
PlacePlus -> AnyWord* Place;
Places -> Place PlacePlus*;
TopicText -> AnyWord* Places AnyWord*;

PlaceTopic -> TopicText interp (Place.Text::not_norm);