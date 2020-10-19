%Testing GY-521 Module to determine position

clc;
close all;
clear;
format compact;

% filename = 'log.csv';
% M = csvread(filename);

T = readtable('log.csv');

ax = table2array(T(:, 2));
ay = table2array(T(:, 3));
az = table2array(T(:, 4));


% cumtrapz

figure;
plot3(ax, ay, az, 'o');
xlabel("X-axis");
ylabel("Y-axis");
zlabel("Z-axis");