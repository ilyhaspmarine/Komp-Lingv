#encoding "utf8"

SquareW -> 'площадь'|'пл.'|'пл' (Punct) (EOSent);

Fallen -> 'павший'<gram="род,мн"> 'борец'<gram="род,мн">;

SquareFull -> SquareW Fallen;