#version 130

in vec4 color;
in vec2 tex_coord;

uniform sampler2D texture;

out vec4 frag_color;


void main(){
    frag_color = color * texture2D(texture, tex_coord * vec2(1, -1));
}