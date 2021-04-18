clc;
clear;
close all;
format compact;

size = 400;

theta = linspace(0, 2*pi, size);

r1 = size * cos(5*theta);
r2 = size * cos(4*theta);
r3 = size * cos(3*theta);
r4 = size * cos(2*theta);


[x1, y1] = pol2cart(theta,r1);
[x2, y2] = pol2cart(theta,r2);
[x3, y3] = pol2cart(theta,r3);
[x4, y4] = pol2cart(theta,r4);
t = 0:size - 1;
data = [t; x1; y1; x2; y2; x3; y3; x4; y4];
data = data.';
data = round(data);

writematrix(data,'rose_data.csv');

figure;
plot(x1, y1, x2, y2, x3, y3, x4, y4);
% xlim([-1, 1]);
% ylim([-1, 1]);