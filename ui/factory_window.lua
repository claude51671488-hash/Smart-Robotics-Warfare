-- Static backgrounds: Button controls use their own state colours.
Root =
{
    Type = "Static",
    Name = "srw_factory_window",
    Style = "Normal",
    Texture = "ui/textures/FE-Panel.dds",
    Colour = { 24, 31, 43, 255 },
    ColourLower = { 24, 31, 43, 255 },
    Control =
    {
        Position = { 160, 50, -100 },
        Size = { 880, 300 },
        Children =
        {
            {
                Type = "Static",
                Name = "srw_map_background",
                Style = "Normal",
                Texture = "ui/textures/FE-Panel.dds",
                Colour = { 9, 16, 25, 255 },
                ColourLower = { 9, 16, 25, 255 },
                Control =
                {
                    Position = { 660, 70, -100 },
                    Size = { 200, 150 },
                },
            },
        },
    },
}
