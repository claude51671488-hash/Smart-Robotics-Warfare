dofile(path.."/weapons/tank_rockets.lua")
Projectile="srw_smith_rocket"
RoundsEachBurst=2
RoundPeriod=0.15
ReloadTime=4.5
MinFireSpeed=3500
MaxFireSpeed=3500.1
MaxFireRadius=7000.0
-- Unguided cassettes rotate the Swarm body toward the ballistic aim point.
-- They do not acquire a seeker or become disabled by seeker-only EMP.
ForceFireAngle=nil
MinFireAngle=-180
MaxFireAngle=180
if Root then
    local body=Root
    body.Name="SwarmCassette"
    body.Angle=90
    for _,node in ipairs(body.ChildrenInFront or {}) do
        if node.Name=="Door" then node.UserData=0 end
    end
    Root={Name="SRWRocketMount",Pivot={0,0},ChildrenInFront={
        {Name="Head",Angle=0,Pivot={0,0},UserData=50,ChildrenInFront={body}}
    }}
end
