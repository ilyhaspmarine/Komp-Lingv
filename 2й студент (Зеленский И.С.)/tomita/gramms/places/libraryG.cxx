#encoding "utf8"

Im -> 'они'<gram="дат"> (Punct) (EOSent)|'имя'<gram="род">|'им.'|'им' (Punct) (EOSent);
LibraryW -> 'библиотека'|'библ.'|'библ' (Punct) (EOSent);
Maxim -> 'м' (Punct) (EOSent)|'максим'<gram="род">|'М.'|'м.';
Gorkiy -> (Maxim)'горький'<gram="род">;

Library -> LibraryW (Im) Gorkiy;